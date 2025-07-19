1) Cenário 
A empresa quer disponibilizar um banco de dados PostgreSQL para uso em 
produção. Temos um time pequeno de dados e esse banco não pode ter downtime. 
Ele será utilizado por colaboradores em São Paulo, Nova York e Londres com alta 
frequência de leitura e gravação. 

1) Resposta
Relacionado a alta frequencia e leitura existe a necessidade de uma base de replica focada em leitura.
Se existir problemas relacionado a latência (aplicações que necessitam de informações atualizadas rapidamente) será necessário
uma arquitetura multi region. Soluções Cloud conseguem nos ajudar com isso. Caso seja apenas queries consultivas para usuários físicos
provavelmente não há necessidade por conta da latência. Mas por se tratar de um banco crítico é interessante realizar um deploy multi region
Particularmente soluções cloud auxiliam muito nessa configuração

https://aws.amazon.com/pt/blogs/database/deploy-multi-region-amazon-aurora-applications-with-a-failover-blueprint/
https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html
https://docs.aws.amazon.com/AmazonRDS/latest/AuroraPostgreSQLReleaseNotes/AuroraPostgreSQL.Updates.html


É importante também ter monitoramentos a nível de recurso computacional, principalmente storage e CPU
Além de uma monitoria de queries que podem estar travando o base, monitorar o número de conexões ativas também é importante
E evitar usuários compartilhados, caso exista algum usuário ofensor é importante isolar o problema rapidamente e não impactar demais usuários/aplicações

Releventa manter uma rotina de backup para disaster recovery


