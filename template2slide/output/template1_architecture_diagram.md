# System Architecture: Video Analytics Solution Proposal for Bromma Malaysia

**Client:** Bromma Malaysia

**Deployment Method:** CLOUD

**Cameras:** 15

**AI Modules:** 7

---

## Architecture Diagram

```mermaid
graph LR
    subgraph "On-Site Infrastructure"
        direction TB
        Cameras["Up to 15 Cameras<br/>IP-based Camera"]
        
        Internet["Internet Connection<br/>(Provided by Client)"]
    end
    
    subgraph "On-Cloud"
        direction LR
        subgraph "Cloud Infrastructure"
            direction TB
            Cloud_Inference["On-cloud in AWS<br/>(viAct's CMP)<br/>Helmet Detection<br/>Safety Mask Detection<br/>Hi-vis vest detection<br/>Fire & Smoke Detection<br/>Worker–Vehicle Anti-collision<br/>Danger Zone / Restricted Zone Monitoring<br/>Human Down Detection"]
        end
        
        subgraph "Output Services"
            direction TB
            Dashboard["Centralized Dashboard"]
            Alert["Alert/Notification<br/>(Email & Telegram & Dashboard)"]
        end
    end
    
    HSE_Manager["HSE Manager"]
    
    Cameras -->|RTSP Links| Internet
    Internet --> Cloud_Inference
    Cloud_Inference --> Dashboard
    HSE_Manager --> Dashboard
    style Cloud_Inference fill:#81d4fa,stroke:#0277bd,stroke-width:3px,color:#000000
    style Dashboard fill:#fff4e1,stroke:#e65100,stroke-width:2px,color:#000000
    style Alert fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000000
    style HSE_Manager fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000000
    style Internet fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000000
    style Cameras fill:#ffffff,stroke:#424242,stroke-width:2px,color:#000000
    classDef aiModuleStyle fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000000

```
