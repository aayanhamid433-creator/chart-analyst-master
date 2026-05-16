import fetch from 'node-fetch';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'POST') {
    try {
      const { imageBase64, pair, timeframe } = req.body;

      if (!imageBase64) {
        return res.status(400).json({ error: 'No image provided' });
      }

      const apiKey = process.env.ANTHROPIC_API_KEY;
      if (!apiKey) {
        return res.status(500).json({ error: 'API key not configured' });
      }

      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey,
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 1500,
          messages: [{
            role: 'user',
            content: [{
              type: 'image',
              source: {
                type: 'base64',
                media_type: 'image/jpeg',
                data: imageBase64,
              },
            }, {
              type: 'text',
              text: `Analyze this trading chart and provide ONLY JSON (no markdown):
{
  "pair": "SYMBOL",
  "timeframe": "1m/5m/15m",
  "trend": "BULLISH/BEARISH/NEUTRAL",
  "patterns_found": ["pattern1"],
  "entry_range": "price range",
  "stop_loss": "price",
  "tp1": "price",
  "tp2": "price",
  "tp3": "price",
  "risk_reward": "1:X",
  "confidence": "0-100",
  "analysis": "2-3 sentences"
}`
            }]
          }]
        })
      });

      if (!response.ok) {
        return res.status(500).json({ error: 'Analysis failed' });
      }

      const data = await response.json();
      const analysisText = data.content[0].text;
      const jsonMatch = analysisText.match(/\{[\s\S]*\}/);
      
      if (!jsonMatch) {
        return res.status(500).json({ error: 'Invalid response' });
      }

      const analysis = JSON.parse(jsonMatch[0]);
      analysis.timestamp = new Date().toISOString();
      analysis.id = Date.now().toString();

      return res.status(200).json(analysis);
    } catch (error) {
      return res.status(500).json({ error: error.message });
    }
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
