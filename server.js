import express from 'express'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import cors from 'cors'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const app = express()
const PORT = 3001

app.use(cors())
app.use(express.json({ limit: '10mb' }))

// Endpoint to save stations.json
app.post('/api/save-stations', (req, res) => {
  try {
    const stationsData = req.body
    const filePath = path.join(__dirname, 'src', 'data', 'stations.json')

    // Write the file
    fs.writeFileSync(filePath, JSON.stringify(stationsData, null, 2), 'utf8')

    console.log('✅ stations.json saved successfully!')
    res.json({ success: true, message: 'File saved successfully!' })
  } catch (error) {
    console.error('❌ Error saving file:', error)
    res.status(500).json({ success: false, message: error.message })
  }
})

app.listen(PORT, () => {
  console.log(`🚀 Save server running on http://localhost:${PORT}`)
  console.log('📁 Ready to save stations.json')
})
