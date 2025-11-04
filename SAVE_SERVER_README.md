# Save Server - Auto-Save Coordinates

## 🎯 Problem Solved
Browsers cannot directly overwrite files on your computer for security reasons. This save server allows the app to automatically save coordinate changes to `stations.json` without the download popup!

## 🚀 How to Use

### Start Both Servers

**Terminal 1 - Main App:**
```bash
npm run dev
```

**Terminal 2 - Save Server:**
```bash
npm run save-server
```

### Usage
1. Both servers must be running
2. Drag markers to new positions in the app
3. Click "💾 Save Coordinates"
4. ✅ File is automatically saved to `src/data/stations.json`
5. **No download popup!**
6. Refresh the page to see the updated positions

## 📋 What's Running

| Server | Port | Purpose |
|--------|------|---------|
| Vite Dev Server | 5174 | Main app |
| Save Server | 3001 | Saves files automatically |

## ✅ Success Messages

- **"✅ Saved! stations.json updated successfully"** - File saved!
- **"❌ Error saving file. Is the save server running?"** - Start the save server

## 🔧 Technical Details

### Save Server (`server.js`)
- Express.js server running on port 3001
- Accepts POST requests to `/api/save-stations`
- Writes directly to `src/data/stations.json`
- Includes CORS for local development

### Frontend Integration
- Uses `fetch()` API to send data to server
- Automatic error handling
- Shows notifications for success/failure

## 🛠️ Alternative: Single Command (Future)

You can use `concurrently` to run both servers with one command:

```bash
npm install -D concurrently
```

Then update `package.json`:
```json
"scripts": {
  "dev:all": "concurrently \"npm run dev\" \"npm run save-server\""
}
```

Then run:
```bash
npm run dev:all
```

## 🐛 Troubleshooting

### Error: "Is the save server running?"
- Make sure you started: `npm run save-server`
- Check port 3001 is not in use

### Changes not appearing?
- Hard refresh the browser (Ctrl+Shift+R)
- Check the file was actually saved in `src/data/stations.json`

### CORS errors?
- Make sure both servers are running on localhost
- Check the save server console for errors

## 📝 Notes

- Save server is **only for development**
- In production, use Supabase database instead
- Keep both terminal windows open while working
- Server logs show when files are saved
