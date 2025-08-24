import fs from "fs";

class StorageRepository {
  DEFAULT_FILE_PATH = "./data.json";
  constructor() {
    this.filePath = this.DEFAULT_FILE_PATH;
    if (!fs.existsSync(this.filePath)) {
      fs.writeFileSync(this.filePath, "[]");
    }
  }

  _load() {
    const data = fs.readFileSync(this.filePath, "utf-8");
    return JSON.parse(data);
  }

  _save(data) {
    fs.writeFileSync(this.filePath, JSON.stringify(data, null, 2));
  }

  add(element) {
    const data = this._load();
    data.push(element);
    this._save(data);
  }

  delete(element) {
    let data = this._load();
    data = data.filter((e) => JSON.stringify(e) !== JSON.stringify(element));
    this._save(data);
  }

  getCurrentEventByEmail(creatorEmail) {
    const events = this._load();
    const now = new Date();
    return events.find(
      (e) => now >= e.start && now <= e.end && e.email === creatorEmail
    );
  }

  getAll() {
    return this._load();
  }
}

export default StorageRepository;