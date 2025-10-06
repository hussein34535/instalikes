export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });

  const { postUrl } = req.body;

  // رجع رد فوري للمستخدم
  res.status(200).json({ message: `✅ الطلب استلم لرابط: ${postUrl}، جاري التنفيذ في الخلفية...` });

  // تنفيذ بسيط في الخلفية (اختياري)
  // يمكنك استخدام postUrl هنا لإجراء عمليات اللايكات الفعلية
  // مثال:
  // await fetch('https://your-server.com/run-likes', { method: 'POST', body: JSON.stringify({ url: postUrl }) });
}
