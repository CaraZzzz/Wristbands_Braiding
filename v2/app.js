// app.js
App({
  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 登录
    wx.login({
      success: res => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
      }
    })
  },
  globalData: {
    userInfo: null,
    // 预定义的颜色选项
    colorOptions: [
      { name: '红色', value: 'R', color: '#FF0000' },
      { name: '蓝色', value: 'B', color: '#0000FF' },
      { name: '绿色', value: 'G', color: '#00FF00' },
      { name: '黄色', value: 'Y', color: '#FFFF00' },
      { name: '白色', value: 'W', color: '#FFFFFF' },
      { name: '黑色', value: 'K', color: '#000000' },
      { name: '紫色', value: 'P', color: '#800080' },
      { name: '橙色', value: 'O', color: '#FFA500' }
    ]
  }
}) 