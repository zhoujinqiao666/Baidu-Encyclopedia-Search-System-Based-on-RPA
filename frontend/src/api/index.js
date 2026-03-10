import axios from 'axios'

const http = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 120000,  // 爬虫耗时较长，设 2 分钟
})

export default http