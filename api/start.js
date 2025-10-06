import fs from "fs";
import path from "path";

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });

  const { post } = req.body || {};
  if (!post) return res.status(400).json({ error: "Post ID مطلوب" });

  const accountsPath = path.join(process.cwd(), "accounts.json");
  const accounts = JSON.parse(fs.readFileSync(accountsPath, "utf-8"));

  const results = accounts.map(acc => ({
    username: acc.username,
    status: "✅ تم استقبال الحساب وجاري التنفيذ"
  }));

  // نحفظ النتائج موقتًا
  const resultsPath = path.join(process.cwd(), "results.json");
  fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));

  return res.status(200).json({ message: "✅ العملية بدأت بنجاح", results });
}
