# Antisubscription C4 Architecture Model

This document provides a lightweight C4 representation of the
Antisubscription system. The model focuses on the context and container levels
which are the most relevant for contributors.

## Context Diagram

```plantuml
@startuml AntisubscriptionContext
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(user, "End User", "Configures mailbox access and reviews reports")
System_Ext(emailProvider, "Email Provider", "IMAP compatible provider such as Gmail or Yandex")
System_Ext(dashboard, "Reporting Tools", "Dashboards or scripts that query the API")
System(antisubscription, "Antisubscription", "Monitors inboxes for subscription notifications")

Rel(user, antisubscription, "Triggers mailbox synchronisation", "HTTPS")
Rel(antisubscription, emailProvider, "Fetch subscription emails", "IMAP over TLS")
Rel(antisubscription, dashboard, "Expose subscription metrics", "JSON/REST")
@enduml
```

## Container Diagram

```plantuml
@startuml AntisubscriptionContainer
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(user, "End User")
System_Ext(emailProvider, "Email Provider")
Container_Boundary(c1, "Antisubscription") {
    Container(api, "Flask API", "Python", "Handles HTTP requests, triggers mailbox ingestion and exposes subscription data")
    Container(worker, "IMAP Ingestion", "Python", "Connects to IMAP, scans emails and persists results")
    ContainerDb(database, "PostgreSQL", "SQL", "Stores subscription events")
}
Container_Ext(reporting, "Dashboards / Scripts", "Varies", "Visualise reports and metrics")

Rel(user, api, "Configures monitoring and fetches data", "HTTPS")
Rel(api, worker, "Triggers ingestion", "Function call")
Rel(worker, emailProvider, "Downloads emails", "IMAP over TLS")
Rel(worker, database, "Stores subscription records", "psycopg2")
Rel(api, database, "Reads subscription records", "psycopg2")
Rel(api, reporting, "Provides API responses", "JSON/REST")
@enduml
```

Both diagrams can be rendered using [PlantUML](https://plantuml.com/) or the
[C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) VS Code extension.
