const app = getApp()

Page({
  data: {
    // 绳子股数
    stringCountRange: [
      { value: 4, label: '4股' },
      { value: 6, label: '6股' },
      { value: 8, label: '8股' },
      { value: 10, label: '10股' },
      { value: 12, label: '12股' }
    ],
    stringCountIndex: 0,
    stringCount: 4,
    // 当前选择的颜色
    selectedColors: [],
    // 目标图案配置
    targetPattern: [],
    // 颜色选项
    colorOptions: app.globalData.colorOptions,
    // 当前编辑的行索引
    currentEditRow: -1,
    // 当前编辑的列索引
    currentEditCol: -1,
    // 是否显示颜色选择器
    showColorPicker: false,
    // 编辑模式：'start' 或 'target'
    editMode: 'start',
    // API配置
    apiBaseUrl: 'http://localhost:5000/api',
    // 新增：自定义颜色选择器所需的状态
    activePicker: {},      // 记录当前激活的是哪个颜色块
    loading: false,
  },

  onLoad() {
    this.initData()
  },

  // 初始化数据
  initData() {
    const newIndex = this.data.stringCountIndex;
    const newStringCount = this.data.stringCountRange[newIndex].value;
    const selectedColors = new Array(newStringCount).fill('');
    this.setData({
      stringCount: newStringCount,
      selectedColors,
      targetPattern: []
    });
  },

  // 改变绳子股数
  onStringCountChange(e) {
    const newIndex = parseInt(e.detail.value, 10);
    const newStringCount = this.data.stringCountRange[newIndex].value;
    const selectedColors = new Array(newStringCount).fill('');
    this.setData({
      stringCountIndex: newIndex,
      stringCount: newStringCount,
      selectedColors,
      targetPattern: []
    });
  },

  // 选择颜色
  onColorSelect(e) {
    const { color } = e.currentTarget.dataset
    const { editMode, currentEditRow, currentEditCol } = this.data

    if (currentEditCol < 0) return;

    const dataToSet = {
      showColorPicker: false,
      currentEditRow: -1,
      currentEditCol: -1
    };

    if (editMode === 'start') {
      dataToSet[`selectedColors[${currentEditCol}]`] = color;
    } else {
      if (currentEditRow < 0) return;
      dataToSet[`targetPattern[${currentEditRow}][${currentEditCol}]`] = color;
    }
    
    this.setData(dataToSet);
  },

  // 显示颜色选择器
  showColorPicker(e) {
    const { mode, row, col } = e.currentTarget.dataset
    this.setData({
      showColorPicker: true,
      editMode: mode,
      currentEditRow: row !== undefined ? row : -1,
      currentEditCol: col !== undefined ? col : -1
    })
  },

  // 隐藏颜色选择器
  hideColorPicker() {
    this.setData({
      showColorPicker: false,
      currentEditRow: -1,
      currentEditCol: -1
    })
  },

  // 添加一行
  addRow() {
    const { targetPattern, stringCount } = this.data;
    if (stringCount < 2) {
      wx.showToast({ title: '请先设置至少2股绳子', icon: 'none' });
      return;
    }
    // 根据当前是奇数行还是偶数行，计算该行应有的结数
    const isNewLineOdd = (targetPattern.length + 1) % 2 !== 0;
    const knotsInRow = Math.floor((stringCount - (isNewLineOdd ? 0 : 1)) / 2);

    if (knotsInRow <= 0) {
      wx.showToast({ title: '此行没有可编的绳结', icon: 'none' });
      return;
    }
    // 新增行默认使用第一个颜色填充
    const newRow = Array(knotsInRow).fill(this.data.colorOptions[0].value);
    targetPattern.push(newRow);
    this.setData({ targetPattern });
  },

  // 删除一行
  removeRow(e) {
    const { rowIndex } = e.currentTarget.dataset;
    const { targetPattern } = this.data;
    targetPattern.splice(rowIndex, 1);
    this.setData({ targetPattern });
  },

  // 为某行添加一个结
  addKnot(e) {
    const { rowIndex } = e.currentTarget.dataset;
    const { targetPattern, stringCount } = this.data;
    
    const isOddLine = (rowIndex + 1) % 2 !== 0;
    const maxKnots = Math.floor((stringCount - (isOddLine ? 0 : 1)) / 2);

    if (targetPattern[rowIndex].length >= maxKnots) {
      wx.showToast({ title: `该行最多只能有 ${maxKnots} 个结`, icon: 'none' });
      return;
    }

    targetPattern[rowIndex].push(this.data.colorOptions[0].value);
    this.setData({ 
      [`targetPattern[${rowIndex}]`]: targetPattern[rowIndex] 
    });
  },

  // 清空所有行
  clearPattern() {
    this.setData({ targetPattern: [] });
  },

  // 目标图案颜色选择变化
  onColorChange(e) {
    const { rowIndex, colIndex } = e.currentTarget.dataset;
    const newColorIndex = e.detail.value;
    const newColorValue = this.data.colorOptions[newColorIndex].value;
    
    this.setData({
      [`targetPattern[${rowIndex}][${colIndex}]`]: newColorValue
    });
  },

  // 验证输入
  validateInput() {
    const { selectedColors, targetPattern, stringCount } = this.data

    // 检查起始颜色是否完整
    if (selectedColors.some(color => !color)) {
      wx.showToast({
        title: '请选择完整的起始颜色',
        icon: 'none'
      })
      return false
    }

    // 检查绳子股数是否为偶数
    if (stringCount % 2 !== 0) {
      wx.showToast({
        title: '绳子股数必须为偶数',
        icon: 'none'
      })
      return false
    }

    // 检查目标图案
    if (targetPattern.length === 0) {
      wx.showToast({
        title: '请设置目标图案',
        icon: 'none'
      })
      return false
    }

    // 检查每行的绳结数量
    for (let i = 0; i < targetPattern.length; i++) {
      const row = targetPattern[i] || [];
      const isOddLine = i % 2 === 0
      const expectedKnots = isOddLine ? Math.floor(stringCount / 2) : Math.floor(stringCount / 2) - 1;
      
      if (row.length !== expectedKnots) {
        wx.showToast({
          title: `第${i + 1}行应有${expectedKnots}个绳结`,
          icon: 'none'
        })
        return false
      }

      // 检查每个绳结是否都有颜色
      if (row.some(color => !color)) {
        wx.showToast({
          title: `第${i + 1}行有未设置颜色的绳结`,
          icon: 'none'
        })
        return false
      }
    }

    return true
  },

  // 生成编织方案
  generateSolution() {
    const { stringCount, selectedColors, targetPattern } = this.data;
    if (!this.validateInput()) {
      return
    }

    // 显示加载提示
    wx.showLoading({
      title: '计算中...'
    })

    // 调用后端API
    this.callKnotAlgorithm(selectedColors, targetPattern)
  },

  // 调用绳结算法API
  callKnotAlgorithm(startState, compositionColor) {
    const { apiBaseUrl } = this.data
    
    wx.request({
      url: `${apiBaseUrl}/generate-knot`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        startState: startState,
        targetPattern: compositionColor
      },
      success: (res) => {
        wx.hideLoading()
        
        if (res.statusCode === 200 && res.data && res.data.bestSolution) {
          wx.navigateTo({
            url: '/pages/result/result',
            success: (navRes) => {
              // 将API返回的结果和用户输入的原始目标图案一起传递给结果页
              navRes.eventChannel.emit('acceptDataFromOpenerPage', { 
                result: { 
                  ...res.data, 
                  targetPattern: compositionColor, // 明确传递用户输入的目标图案
                } 
              })
            }
          })
        } else {
          wx.showToast({
            title: res.data.error || '生成方案失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('API调用失败:', err)
        
        wx.showToast({
          title: 'API调用失败, 请检查后端服务',
          icon: 'none'
        })
      }
    })
  },

  // 获取颜色显示名称
  getColorName(colorValue) {
    const colorOption = this.data.colorOptions.find(option => option.value === colorValue)
    return colorOption ? colorOption.name : colorValue
  },

  // 获取颜色样式
  getColorStyle(colorValue) {
    const colorOption = this.data.colorOptions.find(option => option.value === colorValue)
    return colorOption ? `background-color: ${colorOption.color}` : ''
  },

  // 阻止事件冒泡
  stopPropagation() {
    // 空函数，用于阻止事件冒泡
  },

  // --- 自定义颜色选择器方法 ---

  openColorPicker(e) {
    const { mode, index, rowIndex, colIndex } = e.currentTarget.dataset;
    this.setData({
      showColorPicker: true,
      activePicker: { mode, index, rowIndex, colIndex },
    });
  },

  closeColorPicker() {
    this.setData({ showColorPicker: false });
  },

  // 点击颜色后直接选择并关闭弹窗
  onPopupColorSelect(e) {
    const newColor = e.currentTarget.dataset.color;
    const { activePicker } = this.data;

    if (activePicker.mode === 'initial') {
      this.setData({
        [`selectedColors[${activePicker.index}]`]: newColor,
      });
    } else { // 'target'
      this.setData({
        [`targetPattern[${activePicker.rowIndex}][${activePicker.colIndex}]`]: newColor,
      });
    }
    
    this.closeColorPicker();
  },
}) 