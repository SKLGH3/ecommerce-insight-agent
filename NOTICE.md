# NOTICE

Ecommerce Insight Agent 是基于以下开源项目进行的二次开发：

- 上游项目：didilili/shopkeeper-agent
- 上游地址：https://github.com/didilili/shopkeeper-agent
- 上游许可证：MIT License
- 基线提交：8045fa4d61608f58df551fda6cd1a70529bb5b67

本仓库保留上游项目的 LICENSE 文件与版权声明。

主要二次开发内容包括：

- 项目品牌升级为“电商智能问数平台 / Ecommerce Insight Agent”；
- 增加 AST 级 SQL 只读校验和授权表限制；
- 增加 SQL 修正次数上限、查询超时和结果行数限制；
- 使用独立的元数据库应用账号与数仓只读账号；
- 增加后端、前端生产镜像和完整 Docker Compose 编排；
- 增加输入校验、自动化测试、环境变量模板与部署文档。

除 LICENSE 中明确授予的权利外，上游项目名称及其维护者不对本项目提供背书或保证。
