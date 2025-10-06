export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });

  // رجع رد فوري للمستخدم
  res.status(200).json({ message: '✅ الطلب استلم، جاري التنفيذ في الخلفية...' });

  // تنفيذ بسيط في الخلفية (اختياري)
  // ممكن هنا تبعت طلب لسيرفرك الحقيقي لو بتعمل لايكات فعلاً
  // مثلاً:
  // await fetch('https://your-server.com/run-likes', { method: 'POST' });
}
