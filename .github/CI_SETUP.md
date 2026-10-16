# CI 配置指南

这份文档记录本仓库 GitHub Actions 里**必须手工配置一次**的外部依赖。缺了它们 CI 不会报错，但会静默地留下一堆处理不掉的东西，排查起来很费时间。

---

## SNAPSHOT_TOKEN 配置

### 为什么必须要它

`stars-snapshot.yml` 每周五跑一次，刷新各框架的 star 数据并开一个 PR。这个 PR 曾经长期卡在 open 状态合不进去，根因不是脚本写错，而是 GitHub 的一条机制：

> 由默认 `GITHUB_TOKEN` 触发的事件，**不会再派生新的 workflow run**（用于防止无限递归）。

于是形成死锁：

```
GITHUB_TOKEN 建 PR
    ↓
PR 的 pull_request 事件不触发 Check Links / Smoke Test
    ↓
必需检查永远停在 expected / action_required
    ↓
auto-merge 等不到绿灯
    ↓
PR 永久 open（每周多一个）
```

### 解法

用一个 PAT 来做「建 PR」和「合并」这两个动作。PAT 是真实用户身份，它触发的事件会正常派生 workflow run，必需检查能跑完，auto-merge 才会放行。

### 配置步骤

1. 打开 Personal access tokens 页面（右上角头像 → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token）：

```
https://github.com/settings/personal-access-tokens/new
```

2. 按下表填写：

| 字段 | 值 |
|------|-----|
| Token name | `ai-agent-handbook-ci` |
| Resource owner | `Xwh630` |
| Repository access | **Only select repositories** → 选 `ai-agent-handbook` |
| Expiration | 选最长（1 年），到期前记得续，到期后 snapshot 会重新卡住 |

3. Repository permissions 勾这三项，全部给 **Read and write**：

| 权限 | 级别 |
|------|------|
| Contents | Read and write |
| Pull requests | Read and write |
| Actions | Read and write |

4. 生成后复制 token，回到仓库：

```
https://github.com/Xwh630/ai-agent-handbook/settings/secrets/actions
```

点击 New repository secret，Name 填 `SNAPSHOT_TOKEN`，Secret 粘贴刚才的 token。

### 验证

配置完成后手动跑一次：

```
https://github.com/Xwh630/ai-agent-handbook/actions/workflows/stars-snapshot.yml
```

点 Run workflow，观察生成的 PR：Check Links 与 Examples Smoke Test 应该正常变绿，随后 PR 自动合入。如果它们仍然停在 `action_required`，说明 token 没生效——回到第 3 步检查权限是否漏勾。

---

## 降级行为

没有配置 `SNAPSHOT_TOKEN` 时 workflow 依然会运行，但会：

- 回退使用 `GITHUB_TOKEN`
- 在 workflow 日志里打一条醒目 warning
- 大概率又留一个合不进去的 PR

这是有意保留的行为：宁可见到一个明确的 warning，也不要默默什么都不做。看到这个 warning 就照上面的步骤配一次。

即使已经配置了 PAT，`stars-snapshot.yml` 里仍保留了一个「自愈」步骤：每次运行先检查有没有遗留的 snapshot PR，有就先尝试合并它。所以历史欠账不需要手工清理，跑一轮就自动还清。

---

## 相关已知坑

| 现象 | 原因 | 状态 |
|------|------|------|
| snapshot PR 卡住不合 | 用 GITHUB_TOKEN 建 PR，必需检查不触发 | 已根因修复（换 PAT） |
| 直推 main 被 required checks 拦 | 分支保护规则要求 status checks | 改为 PR + auto-merge 绕开 |
| 每周多个重复 PR | PR 未合，下次运行又开新的 | 自愈步骤会先处理遗留 PR |
