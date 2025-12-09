import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Table,
  Card,
  Button,
  Input,
  Space,
  Tag,
  Statistic,
  Row,
  Col,
  Spin,
  Typography,
  Select,
  Tree,
  Modal,
  Form,
  InputNumber,
  Divider,
  message,
} from 'antd'
import {
  ReloadOutlined,
  UserAddOutlined,
  TrophyOutlined,
  TeamOutlined,
  EyeOutlined,
  SettingOutlined,
  SaveOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import type { ColumnsType } from 'antd/es/table'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { inviteApi } from '../utils/api'
import { useMutation, useQueryClient } from '@tanstack/react-query'

const { Text } = Typography

interface InviteRelation {
  user_id: number
  user_tg_id?: number
  user_username?: string
  user_name?: string
  invite_code?: string
  invite_count: number
  invite_earnings: number
  invited_by_tg_id?: number
  invited_by_username?: string
  invited_by_name?: string
  created_at: string
}

export default function InviteManagement() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [filters, setFilters] = useState({
    inviter_id: undefined as number | undefined,
    invitee_id: undefined as number | undefined,
    min_invites: undefined as number | undefined,
  })
  const [trendDays, setTrendDays] = useState(30)
  const [treeModalVisible, setTreeModalVisible] = useState(false)
  const [treeUserId, setTreeUserId] = useState<number | null>(null)
  const [configForm] = Form.useForm()

  // 获取邀请关系列表
  const { data: listData, isLoading } = useQuery({
    queryKey: ['invites', page, pageSize, filters],
    queryFn: async () => {
      const response = await inviteApi.list({
        page,
        page_size: pageSize,
        inviter_id: filters.inviter_id,
        invitee_id: filters.invitee_id,
        min_invites: filters.min_invites,
      })
      return response.data
    },
  })

  // 获取统计信息
  const { data: statsData } = useQuery({
    queryKey: ['invites-stats'],
    queryFn: async () => {
      const response = await inviteApi.getStats()
      return response.data
    },
  })

  // 获取趋势数据
  const { data: trendData, isLoading: trendLoading } = useQuery({
    queryKey: ['invites-trend', trendDays],
    queryFn: async () => {
      const response = await inviteApi.getTrend({ days: trendDays })
      return response.data
    },
  })

  // 获取邀请关系树
  const { data: treeDataResponse, isLoading: treeLoading } = useQuery({
    queryKey: ['invite-tree', treeUserId],
    queryFn: async () => {
      const response = await inviteApi.getTree(treeUserId!, 3)
      return response.data
    },
    enabled: treeModalVisible && treeUserId !== null,
  })

  // 获取佣金配置
  const { data: configData, refetch: refetchConfig } = useQuery({
    queryKey: ['commission-config'],
    queryFn: async () => {
      const response = await inviteApi.getCommissionConfig()
      return response.data
    },
  })

  // 更新佣金配置
  const updateConfigMutation = useMutation({
    mutationFn: async (values: any) => {
      const response = await inviteApi.updateCommissionConfig(values)
      return response.data
    },
    onSuccess: () => {
      message.success('佣金配置更新成功')
      refetchConfig()
    },
    onError: (error: any) => {
      message.error(`更新失败: ${error.message}`)
    },
  })

  const handleViewTree = (userId: number) => {
    setTreeUserId(userId)
    setTreeModalVisible(true)
  }

  const buildTreeNodes = (data: any): any[] => {
    if (!data) return []
    
    const node = {
      title: (
        <div>
          <div>{data.user.user_name || data.user.user_username || `ID: ${data.user.user_id}`}</div>
          <div style={{ fontSize: 12, color: '#999' }}>
            TG: {data.user.user_tg_id} | 邀请: {data.user.invite_count} 人 | 收益: {data.user.invite_earnings}
          </div>
        </div>
      ),
      key: data.user.user_id,
      children: data.children ? data.children.map((child: any) => buildTreeNodes(child)) : [],
    }
    
    return [node]
  }

  const columns: ColumnsType<InviteRelation> = [
    {
      title: '用户ID',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 100,
    },
    {
      title: '用户',
      key: 'user',
      width: 200,
      render: (_, record) => (
        <div>
          <div>{record.user_name || record.user_username || `ID: ${record.user_id}`}</div>
          {record.user_tg_id && (
            <div style={{ fontSize: 12, color: '#999' }}>TG: {record.user_tg_id}</div>
          )}
        </div>
      ),
    },
    {
      title: '邀请码',
      dataIndex: 'invite_code',
      key: 'invite_code',
      width: 120,
      render: (code) => code ? <Tag color="blue">{code}</Tag> : '-',
    },
    {
      title: '邀请人数',
      dataIndex: 'invite_count',
      key: 'invite_count',
      width: 100,
      render: (count) => <Tag color="green">{count} 人</Tag>,
    },
    {
      title: '邀请收益',
      dataIndex: 'invite_earnings',
      key: 'invite_earnings',
      width: 120,
      render: (earnings) => (
        <Text strong style={{ color: '#52c41a' }}>
          {Number(earnings).toFixed(2)}
        </Text>
      ),
    },
    {
      title: '邀请人',
      key: 'inviter',
      width: 200,
      render: (_, record) => {
        if (record.invited_by_tg_id) {
          return (
            <div>
              <div>{record.invited_by_name || record.invited_by_username || `TG: ${record.invited_by_tg_id}`}</div>
              <div style={{ fontSize: 12, color: '#999' }}>TG: {record.invited_by_tg_id}</div>
            </div>
          )
        }
        return <Text type="secondary">无</Text>
      },
    },
    {
      title: '注册时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      fixed: 'right',
      render: (_, record) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => handleViewTree(record.user_id)}
        >
          查看关系树
        </Button>
      ),
    },
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>邀请管理</h1>

      {/* 统计卡片 */}
      {statsData && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总邀请数"
                value={statsData.total_invites}
                prefix={<UserAddOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="总邀请收益"
                value={Number(statsData.total_earnings).toFixed(2)}
                prefix={<TrophyOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="活跃邀请人"
                value={statsData.active_inviters}
                prefix={<TeamOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="平均邀请数"
                value={statsData.average_invites}
                prefix={<UserAddOutlined />}
                suffix="人/人"
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 顶级邀请人 */}
      {statsData?.top_inviter && (
        <Card style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={24}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <TrophyOutlined style={{ fontSize: 24, color: '#faad14' }} />
                <div>
                  <div style={{ fontSize: 16, fontWeight: 'bold' }}>顶级邀请人</div>
                  <div style={{ marginTop: 8 }}>
                    <Text strong>{statsData.top_inviter.user_name || statsData.top_inviter.user_username}</Text>
                    <Text type="secondary" style={{ marginLeft: 16 }}>
                      TG: {statsData.top_inviter.user_tg_id}
                    </Text>
                    <Tag color="gold" style={{ marginLeft: 16 }}>
                      邀请 {statsData.top_inviter.invite_count} 人
                    </Tag>
                    <Tag color="green" style={{ marginLeft: 8 }}>
                      收益 {Number(statsData.top_inviter.invite_earnings).toFixed(2)}
                    </Tag>
                  </div>
                </div>
              </div>
            </Col>
          </Row>
        </Card>
      )}

      {/* 统计图表 */}
      <Card
        title={
          <Space>
            <TeamOutlined />
            <span>邀请趋势分析</span>
          </Space>
        }
        style={{ marginBottom: 16 }}
        extra={
          <Select
            value={trendDays}
            onChange={setTrendDays}
            style={{ width: 120 }}
          >
            <Select.Option value={7}>最近7天</Select.Option>
            <Select.Option value={30}>最近30天</Select.Option>
            <Select.Option value={90}>最近90天</Select.Option>
            <Select.Option value={365}>最近1年</Select.Option>
          </Select>
        }
      >
        {trendLoading ? (
          <div style={{ textAlign: 'center', padding: 50 }}>
            <Spin />
          </div>
        ) : trendData ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData.dates?.map((date: string, index: number) => ({
              date: dayjs(date).format('MM-DD'),
              new_users: trendData.new_users?.[index] || 0,
            })) || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="new_users" stroke="#8884d8" name="新用户数" />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div style={{ textAlign: 'center', padding: 50 }}>
            <Text type="secondary">暂无数据</Text>
          </div>
        )}
      </Card>

      {/* 佣金配置 */}
      <Card
        title={
          <span>
            <SettingOutlined /> 佣金配置
          </span>
        }
        style={{ marginBottom: 24 }}
      >
        <Form
          form={configForm}
          layout="vertical"
          initialValues={configData || {
            tier1_commission: 5.0,
            tier2_commission: 2.0,
            tier3_commission: 0.0,
            agent_bonus_threshold: 100,
            agent_bonus_amount: 50.0,
            kol_bonus_threshold: 100,
            kol_bonus_amount: 50.0,
          }}
          onFinish={(values) => {
            updateConfigMutation.mutate(values)
          }}
        >
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="一级佣金率 (%)"
                name="tier1_commission"
                rules={[{ required: true, message: '请输入一级佣金率' }]}
              >
                <InputNumber
                  min={0}
                  max={100}
                  step={0.1}
                  style={{ width: '100%' }}
                  addonAfter="%"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="二级佣金率 (%)"
                name="tier2_commission"
                rules={[{ required: true, message: '请输入二级佣金率' }]}
              >
                <InputNumber
                  min={0}
                  max={100}
                  step={0.1}
                  style={{ width: '100%' }}
                  addonAfter="%"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="三级佣金率 (%)"
                name="tier3_commission"
              >
                <InputNumber
                  min={0}
                  max={100}
                  step={0.1}
                  style={{ width: '100%' }}
                  addonAfter="%"
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Divider>代理奖励配置</Divider>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="代理奖励阈值（邀请用户数）"
                name="agent_bonus_threshold"
                rules={[{ required: true, message: '请输入代理奖励阈值' }]}
              >
                <InputNumber
                  min={1}
                  style={{ width: '100%' }}
                  addonAfter="人"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="代理奖励金额"
                name="agent_bonus_amount"
                rules={[{ required: true, message: '请输入代理奖励金额' }]}
              >
                <InputNumber
                  min={0}
                  step={0.01}
                  style={{ width: '100%' }}
                  addonAfter="USDT"
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Divider>KOL奖励配置</Divider>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="KOL奖励阈值（邀请用户数）"
                name="kol_bonus_threshold"
                rules={[{ required: true, message: '请输入KOL奖励阈值' }]}
              >
                <InputNumber
                  min={1}
                  style={{ width: '100%' }}
                  addonAfter="人"
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="KOL奖励金额"
                name="kol_bonus_amount"
                rules={[{ required: true, message: '请输入KOL奖励金额' }]}
              >
                <InputNumber
                  min={0}
                  step={0.01}
                  style={{ width: '100%' }}
                  addonAfter="USDT"
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              icon={<SaveOutlined />}
              loading={updateConfigMutation.isPending}
            >
              保存配置
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* 筛选栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Input
            placeholder="邀请人ID"
            style={{ width: 120 }}
            type="number"
            value={filters.inviter_id}
            onChange={(e) => setFilters({ ...filters, inviter_id: e.target.value ? Number(e.target.value) : undefined })}
            allowClear
          />
          <Input
            placeholder="被邀请人ID"
            style={{ width: 120 }}
            type="number"
            value={filters.invitee_id}
            onChange={(e) => setFilters({ ...filters, invitee_id: e.target.value ? Number(e.target.value) : undefined })}
            allowClear
          />
          <Input
            placeholder="最少邀请数"
            style={{ width: 120 }}
            type="number"
            value={filters.min_invites}
            onChange={(e) => setFilters({ ...filters, min_invites: e.target.value ? Number(e.target.value) : undefined })}
            allowClear
          />
          <Button
            icon={<ReloadOutlined />}
            onClick={() => {
              setFilters({
                inviter_id: undefined,
                invitee_id: undefined,
                min_invites: undefined,
              })
            }}
          >
            重置
          </Button>
        </Space>
      </Card>

      {/* 表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={listData?.items || []}
          loading={isLoading}
          rowKey="user_id"
          scroll={{ x: 1200 }}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: listData?.total || 0,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (newPage, newPageSize) => {
              setPage(newPage)
              setPageSize(newPageSize)
            },
          }}
        />
      </Card>

      {/* 邀请关系树模态框 */}
      <Modal
        title="邀请关系树"
        open={treeModalVisible}
        onCancel={() => {
          setTreeModalVisible(false)
          setTreeUserId(null)
        }}
        footer={null}
        width={800}
      >
        {treeLoading ? (
          <div style={{ textAlign: 'center', padding: 50 }}>
            <Spin />
          </div>
        ) : treeDataResponse ? (
          <Tree
            treeData={buildTreeNodes(treeDataResponse)}
            defaultExpandAll
          />
        ) : (
          <div style={{ textAlign: 'center', padding: 50 }}>
            <Text type="secondary">暂无数据</Text>
          </div>
        )}
      </Modal>
    </div>
  )
}

