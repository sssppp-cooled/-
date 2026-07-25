# 出口IP

| CIDR | 起始IP | 结束IP | 可用IP总数 |
| --- | ---: | ---: | ---: |
| 54.174.62.128/26 | 54.174.62.128 | 54.174.62.191 | 64个 |
| 143.244.87.0/25 | 143.244.87.0 | 143.244.87.127 | 128个 |

## API 返回 (200 OK)

```json
{
  "results": [
    {
      "cidr": "54.174.62.128/26",
      "direction": "EGRESS",
      "service": "API",
      "description": "API & 3rd party integrations"
    },
    {
      "cidr": "143.244.87.0/25",
      "direction": "EGRESS",
      "service": "API",
      "description": "API & 3rd party integrations"
    }
  ]
}
```

备注：文件名为“出口IP”。如需我帮你把该文件提交并推送到远程仓库，请回复“推送”。
