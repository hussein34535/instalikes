import fs from "fs";
import path from "path";

export default function handler(req, res) {
  const resultsPath = path.join(process.cwd(), "results.json");

  if (!fs.existsSync(resultsPath)) {
    return res.status(200).json({ results: [] });
  }

  const results = JSON.parse(fs.readFileSync(resultsPath, "utf-8"));
  return res.status(200).json({ results });
}
