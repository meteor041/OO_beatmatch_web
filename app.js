const express = require("express");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const {exec} = require("child_process");
const cors = require('cors');
const app = express();
const port = 3000;

app.use(cors());

// 设置上传文件存储路径和文件名
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "uploads/"); // 文件存储目录
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + "-" + file.originalname); // 文件名
  },
});

const upload = multer({ storage });

// 静态文件服务
app.use(express.static(path.join(__dirname, 'public')));

app.use(express.json());

// API：获取文件夹内容
app.get('/log', (req, res) => {
  const folderPath = req.query.path || path.join(__dirname, "beat_log");
  const absolutePath = path.resolve(folderPath);

  // 检查路径是否存在
  if (!fs.existsSync(absolutePath)) {
      return res.status(404).json({ error: 'Folder not found' });
  }

  // 读取文件夹内容
  fs.readdir(absolutePath, { withFileTypes: true }, (err, files) => {
      if (err) {
          return res.status(500).json({ error: 'Unable to read folder' });
      }

      // 返回文件夹和文件信息
      const result = files.map(file => ({
          name: file.name,
          type: file.isDirectory() ? 'folder' : 'file',
          path: path.join(absolutePath, file.name),
      }));
      res.json(result);
  });
});

// 文件上传路由
app.post("/upload", upload.single("file"), (req, res) => {
  if (!req.file) {
    return res.status(400).send("No file uploaded.");
  }
  res.send(`File uploaded: ${req.file.filename}`);
});

// API：下载log文件
app.get('/download-log', (req, res) => {
    const filePath = req.query.path;
    const absolutePath = path.resolve(filePath);

    // 检查文件是否存在
    if (!fs.existsSync(absolutePath)) {
        return res.status(404).send('File not found');
    }

    // 设置响应头，触发浏览器下载
    res.download(absolutePath, (err) => {
        if (err) {
            console.error('Download failed:', err);
            res.status(500).send('Unable to download file');
        }
    });
});

// 文件下载路由
app.get("/download/:filename", (req, res) => {
  const filePath = path.join(__dirname, "uploads", req.params.filename);
  if (fs.existsSync(filePath)) {
    res.download(filePath); // 提供文件下载
  } else {
    res.status(404).send("File not found.");
  }
});

// 删除文件路由
app.delete("/delete/:filename", (req, res) => {
  const filePath = path.join(__dirname, "uploads", req.params.filename);
  console.log(__dirname);
  if (fs.existsSync(filePath)) {
    fs.unlink(filePath, (err) => {
      if (err) {
        return res.status(500).send("Unable to delete file.");
      }
      res.send(`File deleted: ${req.params.filename}`);
    });
  } else {
    res.status(404).send("File not found.");
  }
});

// 启动服务器
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});

// 获取文件列表路由
app.get("/files", (req, res) => {
  fs.readdir("uploads/", (err, files) => {
    if (err) {
      return res.status(500).send("Unable to scan files.");
    }
    res.json(files);
  });
});

// 允许解析JSON请求体
app.use(express.json());

// 执行 Python 文件路由
app.post("/run", (req, res) => {
  const dataCount = req.body.count; // 获取前端传递的 count 参数

//   验证参数是否为有效数字
//  if (isNaN(dataCount) || dataCount < 1) {
// 	dataCount=1;
//  return res.status(400).send("Invalid data count parameter.");
//   }

  // 执行 Python 文件
const pythonScriptPath = '/var/www/beatmatch/src/jar_beat3.py';  
exec(`python3 /var/www/beatmatch/src/jar_beat3.py --count=${dataCount}`, (error, stdout, stderr) => {
  console.log("python module connected");
    if (error) {
      console.error(`!!!Error executing Python script: ${error.message}`);
      return res.status(500).send("Error executing Python script.");
    }
    if (stderr) {
      console.error(`Python script stderr: ${stderr}`);
      return res.status(500).send("Python script returned an error.");
    }
    console.log(`Python script output: ${stdout}`);
    // console.log("Hex representation of stdout:", Buffer.from(stdout).toString("hex"));
    // 将换行符替换为 <br>
    // const formattedOutput = stdout.replace(/\n/g, "<br>");

    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.send(`${stdout}`);
  });
});
