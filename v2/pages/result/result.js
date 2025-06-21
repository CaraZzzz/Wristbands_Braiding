const app = getApp()

Page({
  data: {
    result: null,
    // diagramData 将存储交错的步骤: [State, KnotStep, State, KnotStep, ...]
    diagramData: [], 
    inputInfo: null, // 新增：用于存储输入信息卡片的数据

    // 映射打结方式到符号 (不再包含颜色推算逻辑)
    knotInfoMap: {
      '右右': { symbol: '\\' },
      '左左': { symbol: '/' },
      '左右': { symbol: '<' },
      '右左': { symbol: '>' },
    }
  },

  onLoad(options) {
    const eventChannel = this.getOpenerEventChannel()
    // 增加健壮性检查，确保 eventChannel 存在且不为空对象
    if (eventChannel && Object.keys(eventChannel).length) {
      eventChannel.on('acceptDataFromOpenerPage', (data) => {
        if (data.result) {
          const diagramData = this.generateDiagramData(data.result);
          const inputInfo = this.generateInputInfoData(data.result);
          this.setData({
            result: data.result,
            diagramData: diagramData,
            inputInfo: inputInfo
          })
        }
      })
    } else {
      // 用于开发和调试：如果没有数据传入，则使用一套模拟数据来渲染页面
      console.warn("未通过 eventChannel 接收到数据，已加载模拟数据用于调试。");
      const mockResult = {
        "bestSolution": [
          ["右右", "左左"],
          ["右左"]
        ],
        "startState": ["R", "G", "B", "Y"],
        "statesPath": [
          ["R", "G", "B", "Y"],
          ["G", "R", "Y", "B"],
          ["G", "Y", "R", "B"],
        ],
        "targetState": ["G", "Y", "R", "B"]
      };
      const diagramData = this.generateDiagramData(mockResult);
      const inputInfo = this.generateInputInfoData(mockResult);
      this.setData({
        result: mockResult,
        diagramData: diagramData,
        inputInfo: inputInfo
      });
    }
  },

  /**
   * 生成"输入信息"卡片所需的数据
   * @param {object} result - 后端返回的完整结果
   * @returns {object|null} - 用于渲染输入信息的数据
   */
  generateInputInfoData(result) {
    if (!result) return null;

    // 直接使用从首页传递过来的 startState 和 targetPattern
    const { startState, targetPattern } = result; 
    const colorMap = app.globalData.colorOptions.reduce((map, item) => {
      map[item.value] = item.color;
      return map;
    }, {});
    
    // 直接将 targetPattern 中的颜色值 ('R', 'G'...) 映射为十六进制颜色码
    const targetKnots = targetPattern.map(row => 
      row.map(colorValue => colorMap[colorValue] || '#000000')
    );

    const formattedStartState = startState.map(colorValue => colorMap[colorValue] || '#000000');

    return {
        startState: formattedStartState,
        targetKnots: targetKnots
    };
  },

  /**
   * 生成新的、用于交错显示的图表数据
   * @param {object} result - 后端返回的完整结果
   * @returns {array} - 交错的 [State, KnotStep, State, ...] 数组
   */
  generateDiagramData(result) {
    if (!result || !result.bestSolution) return [];
    
    // 同时解构出 targetPattern，作为颜色来源
    let { statesPath, bestSolution, targetPattern } = result;

    // 防御性编程：确保 statesPath 的长度是正确的（步骤数 + 1）
    // 这将修正"多出一行状态"的问题
    if (statesPath.length > bestSolution.length + 1) {
      console.warn(`数据不一致：statesPath 长度 (${statesPath.length}) 大于 bestSolution.length + 1 (${bestSolution.length + 1})。已截断。`);
      statesPath = statesPath.slice(0, bestSolution.length + 1);
    }
    
    const diagram = [];
    const colorMap = app.globalData.colorOptions.reduce((map, item) => {
      map[item.value] = item.color;
      return map;
    }, {});

    // 基于修正后的 statesPath 长度进行循环
    for (let i = 0; i < statesPath.length; i++) {
      // 1. 添加状态行，并将颜色预先转换为十六进制值，以修复上色问题
      const stateColorsHex = statesPath[i].map(c => colorMap[c] || '#000000');
      diagram.push({
        type: 'state',
        stateNumber: i,
        colors: stateColorsHex
      });

      // 2. 如果后面还有编织步骤，则添加
      if (i < bestSolution.length) {
        const rowKnots = bestSolution[i];
        const currentState = statesPath[i];
        const isOddRow = i % 2 === 0; // 0-indexed row number, so 0 is the 1st row (odd)
        
        const knotStep = {
          type: 'knot_step',
          stepNumber: i + 1,
          slots: []
        };
        
        let stringCursor = 0;
        let knotIndex = 0; // 新增：追踪当前是行内的第几个结

        // 对于偶数编织行 (如第2、4行)，行首会有一个未参与编织的"穿过"绳
        if (!isOddRow) {
          knotStep.slots.push({ type: 'passthrough' });
          stringCursor++;
        }

        // 循环处理当前行的所有真实绳结
        for (const knotType of rowKnots) {
          if (stringCursor + 1 >= currentState.length) continue;
          
          const knotInfo = this.data.knotInfoMap[knotType];
          
          if (knotInfo) {
            // 关键修正：直接从 targetPattern 获取结的颜色
            const knotColorValue = targetPattern[i][knotIndex];

            knotStep.slots.push({
              type: 'knot',
              symbol: knotInfo.symbol,
              color: colorMap[knotColorValue] || '#000000'
            });
          }
          stringCursor += 2;
          knotIndex++; // 移动到下一个结
        }

        // 对于偶数编织行，行末也可能有一个"穿过"绳
        if (!isOddRow && stringCursor < statesPath[i].length) {
            knotStep.slots.push({ type: 'passthrough' });
        }

        diagram.push(knotStep);
      }
    }
    return diagram;
  },

  // 返回首页
  goBack() {
    wx.navigateBack()
  },

  // 分享结果
  onShareAppMessage() {
    return {
      title: '手绳编织方案',
      path: '/pages/index/index'
    }
  }
}) 