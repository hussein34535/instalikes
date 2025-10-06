import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  const filePath = path.join(process.cwd(), 'results.json');

  // لو الملف مش موجود نعمله
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, JSON.stringify({ likes_done: 0 }));
  }

  const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  res.status(200).json(data);
}
