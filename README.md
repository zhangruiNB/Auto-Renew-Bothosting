## 🚀 Bot-hosting 自动续期（GitHub Actions）

这是一个基于 GitHub Actions 的自动化脚本，用于定时登录自动续期 [Bot-hosting](https://bot-hosting.net) 服务。

⚠️ 有 CF 盾，机房 IP 可能被拦截，建议使用稍微干净的代理节点，例如住宅代理。

━━━━━━━━━━━━━━━━━━━━━━

### 💡 重要更新说明
1. **支持账号密码登录（推荐）**：Bot-hosting 控制台已支持设置账号独立密码。相比 Discord Token（容易过期、失效或触发 Discord 风控验证），**账号密码登录永久免维护、最稳定**。
2. **页面变动适配**：同步官方最新变动，适配了新版控制台账单路径（`/dash/billings`）、多种到期日期格式以及最新的续期按钮选择器与 Turnstile 人机验证流程。
3. **多重兼容机制**：保留 `SESSION_TOKEN` Cookie 与 `DISCORD_TOKEN` OAuth 作为备用方案，实现平滑过渡。

━━━━━━━━━━━━━━━━━━━━━━

### 🔐 Secrets 配置说明

| Secret 名称         | 是否必填 | 说明                                                              |
|---------------------|----------|-------------------------------------------------------------------|
| EMAIL              | ✅ 必填  | 登录使用的账号邮箱（也是通知展示的账户）                                |
| PASSWORD           | 🌟 推荐  | 登录密码（推荐必填，可在控制台右上角头像 ➡ Settings 里设置）             |
| SESSION_TOKEN      | ❌ 可选  | Bot-hosting `session_token`，Cookie 方式登录（备用）                  |
| DISCORD_TOKEN      | ❌ 可选  | Discord Token，当未提供密码且 SESSION_TOKEN 失效时走 OAuth 登录（备用）|
| GH_TOKEN           | ❌ 可选  | GitHub (classic) PAT，用于更新失效的 session_token，以 `ghp_` 开头      |
| NODE_LINK          | ❌ 可选  | 代理节点链接（支持 vless://, vmess://, trojan://, hysteria2://, socks5:// 等）|
| TG_BOT_TOKEN       | ❌ 可选  | Telegram Bot Token（用于推送续期结果通知）                            |
| TG_CHAT_ID         | ❌ 可选  | Telegram Chat ID（接收通知的用户或群组 ID）                           |

━━━━━━━━━━━━━━━━━━━━━━

## 部署步骤
1. **Fork 本仓库** 到你自己的 GitHub 账号。
2. 在仓库的 `Settings` ➡ `Secrets and variables` ➡ `Actions` 中添加上方所需的 Secrets。
   - **强烈推荐**：添加 `EMAIL` 与 `PASSWORD` 即可实现全自动长期稳定运行。
3. 进入 `Actions` 页面，点击左侧工作流，允许并手动触发一次 `Run workflow` 测试。
4. 根据你的服务到期周期，可以在 [.github/workflows/renew.yml](.github/workflows/renew.yml) 中调整定时 cron 表达式。

---

### 🔑 如何设置 PASSWORD（推荐）
1. 打开并登录 [Bot-hosting.net](https://bot-hosting.net) 控制台。
2. 点击右上角用户头像 ➡ 进入 `Settings` / `Account` 页面。
3. 找到密码（Password）设置选项，为你的账户设置一个登录密码。
4. 将该密码填入 GitHub Secrets 的 `PASSWORD`。

---

### 🍪 备用：SESSION_TOKEN 获取方法
1. 登录你的 Bot-hosting 账号。
2. 按 `F12` 打开开发者工具 ➡ 选择 `应用程序`（Application） ➡ `Cookie` ➡ `https://bot-hosting.net`。
3. 找到名为 `session_token` 的字段并复制其值。

---

### 💬 备用：DISCORD_TOKEN 获取方法
1. 浏览器打开并登录 Discord 网页版。
2. 按 `F12` 打开开发者工具 ➡ 点击 `网络`（Network） 选项卡。
3. 随意点击任意频道或发送消息，在请求列表中找到任意发往 `discord.com/api` 的请求。
4. 在请求标头中找到 `Authorization` 字段，其对应的值即为 Discord Token。

---

### 🎫 备用：GH_TOKEN 获取方法 (用于自动更新 SESSION_TOKEN)
1. 点击 GitHub 头像 ➡ `Settings` ➡ 底部 `Developer settings`。
2. 点击 `Personal access tokens` ➡ `Tokens (classic)` ➡ `Generate new token (classic)`。
3. 权限勾选 `repo`（或 actions 权限），生成后复制并保存到 Secrets `GH_TOKEN`。

━━━━━━━━━━━━━━━━━━━━━━

## 常见问题与注意事项
* 登录 Bot-hosting 遇到 CF 验证码时，脚本内置了基于底层坐标模拟与 CDP 的 Turnstile 求解方案。若 GitHub Actions 原生机房 IP 被严格风控拦截，请配置 `NODE_LINK` 住宅或干净代理。
* 工作流仅在运行失败时上传调试排错截图，且保留天数限制为 1 天，不会过多占用 GitHub 存储限额。
* 脚本每次运行后会自动清理临时进程并滚动清理历史 Actions 记录，保持仓库整洁。

## ⚠️ 免责声明
* 本项目仅供个人学习与自动化运维参考，非盈利目的，转载请注明来源。
* 使用本脚本请遵守相关服务商的使用条款（Terms of Service）以及所在地区的法律法规。
