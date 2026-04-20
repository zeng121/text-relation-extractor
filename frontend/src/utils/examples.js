export const EXAMPLES = {
  default:
    '2026年4月18日上午9点，星澜科技在上海张江办公室召开了“Atlas 知识中台”项目周会。项目负责人李明表示，该项目由星澜科技与复旦大学计算机学院联合推进，目标是在2026年7月底前完成第一阶段交付。会上，算法工程师周琪汇报说，团队已经完成了医疗文献数据清洗，共处理了12万篇中文论文，主要来自知网和万方数据库。产品经理陈雨提出，第一版系统将服务于华东医院和瑞金医院两个试点客户，核心功能包括实体识别、关系抽取、事件时间线生成和可视化问答。李明还提到，公司计划在5月10日前采购两台 NVIDIA H100 服务器，预算总额为280万元，采购负责人是供应链经理王涛。会议最后决定，由周琪在4月25日前提交关系抽取模型评估报告，由陈雨负责在4月28日与华东医院信息科主任赵文杰确认接口规范。',
  startup:
    '陈晨在星火科技担任产品经理。上个月她和赵磊一起推进增长系统，随后孙宁加入，负责数据分析和运营计划。',
  campus:
    '李华在清华大学人工智能协会负责活动策划。上周王敏加入迎新项目，后来赵宁也参与，负责海报设计。',
};

export const DEFAULT_GRAPH_DATA = {
  nodes: [
    { id: '李明', label: '李明', type: 'person', description: '项目负责人' },
    {
      id: '星澜科技',
      label: '星澜科技',
      type: 'organization',
      description: '项目牵头公司',
    },
    {
      id: 'Atlas 知识中台',
      label: 'Atlas 知识中台',
      type: 'project',
      description: '知识中台项目',
    },
    {
      id: '复旦大学计算机学院',
      label: '复旦大学计算机学院',
      type: 'organization',
      description: '联合推进单位',
    },
    {
      id: '周琪',
      label: '周琪',
      type: 'person',
      description: '算法工程师',
    },
    {
      id: '陈雨',
      label: '陈雨',
      type: 'person',
      description: '产品经理',
    },
    {
      id: '王涛',
      label: '王涛',
      type: 'person',
      description: '供应链经理',
    },
    {
      id: '华东医院',
      label: '华东医院',
      type: 'organization',
      description: '试点客户',
    },
    {
      id: '瑞金医院',
      label: '瑞金医院',
      type: 'organization',
      description: '试点客户',
    },
    {
      id: 'NVIDIA H100 服务器',
      label: 'NVIDIA H100 服务器',
      type: 'hardware',
      description: '计划采购两台',
    },
    {
      id: '关系抽取模型评估报告',
      label: '关系抽取模型评估报告',
      type: 'document',
      description: '待提交报告',
    },
    {
      id: '接口规范',
      label: '接口规范',
      type: 'spec',
      description: '医院对接规范',
    },
    {
      id: '赵文杰',
      label: '赵文杰',
      type: 'person',
      description: '华东医院信息科主任',
    },
  ],
  edges: [
    { source: '李明', target: '星澜科技', label: '任职于' },
    { source: '李明', target: 'Atlas 知识中台', label: '负责' },
    { source: '星澜科技', target: '复旦大学计算机学院', label: '联合推进' },
    { source: '周琪', target: 'Atlas 知识中台', label: '参与' },
    { source: '陈雨', target: 'Atlas 知识中台', label: '参与' },
    { source: 'Atlas 知识中台', target: '华东医院', label: '服务试点' },
    { source: 'Atlas 知识中台', target: '瑞金医院', label: '服务试点' },
    { source: '王涛', target: 'NVIDIA H100 服务器', label: '采购' },
    { source: '周琪', target: '关系抽取模型评估报告', label: '提交' },
    { source: '陈雨', target: '接口规范', label: '确认' },
    { source: '赵文杰', target: '接口规范', label: '确认' },
  ],
  timeline: [
    {
      id: 't1',
      label: 'Atlas 项目周会召开',
      time: '2026年4月18日上午9点',
      detail: '星澜科技在上海张江办公室召开 Atlas 知识中台项目周会。',
      related_nodes: ['星澜科技', 'Atlas 知识中台', '李明'],
    },
    {
      id: 't2',
      label: '采购 H100 服务器',
      time: '2026年5月10日前',
      detail:
        '公司计划采购两台 NVIDIA H100 服务器，预算总额为280万元，由王涛负责。',
      related_nodes: ['星澜科技', '王涛', 'NVIDIA H100 服务器'],
    },
    {
      id: 't3',
      label: '提交模型评估报告',
      time: '2026年4月25日前',
      detail: '周琪需在4月25日前提交关系抽取模型评估报告。',
      related_nodes: ['周琪', '关系抽取模型评估报告'],
    },
    {
      id: 't4',
      label: '确认接口规范',
      time: '2026年4月28日',
      detail: '陈雨将与华东医院信息科主任赵文杰确认接口规范。',
      related_nodes: ['陈雨', '赵文杰', '接口规范', '华东医院'],
    },
  ],
};
