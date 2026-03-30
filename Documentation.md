# Security and Privacy Documentation

## System Overview
This project is a full-stack medical appointment management application with:

- a React + Vite frontend
- a Spring Boot backend
- a PostgreSQL database

The two main domain entities are:

- `Patient`
- `Appointment`

The main supported operations are:

- patient registration and update
- appointment creation, update, deletion, and search
- patient and appointment information retrieval

## Data Flow Diagrams

### DFD Notation Used
The diagrams use standard DFD-inspired notation adapted to the project context:

- **Rectangle**: external entity  
  Represents an actor outside the system boundary that exchanges data with the system.  
  In this project, the main external entity is the `Patient`.

- **Circle / rounded process node**: process  
  Represents an internal system function that transforms, validates, stores, or retrieves data.  
  Examples in this project are `Manage Patient Data`, `Manage Appointments`, and `Search and View Information`.

- **Cylinder**: data store  
  Represents where information is logically stored.  
  In this project, the logical data stores are `Patient Records` and `Appointment Records`.

- **Arrow / labeled relation**: data flow  
  Represents the movement of data between external entities, processes, and data stores.  
  The label describes what is flowing, for example `Profile data`, `Appointment request`, or `Patient record data`.

### Level 0 – Context Diagram
The Level 0 DFD presents the system as a single process. Its goal is to show the overall system boundary and the high-level data exchanged with the external actor.

In this project:

- the external entity is the `Patient`
- the whole application is represented as `Medical Appointment Management System`
- the incoming flows represent patient data and appointment requests
- the outgoing flows represent patient information and appointment details

Current diagram file:

- `src/Diagrams/DFD0.png`

Diagram preview:

![DFD Level 0](src/Diagrams/DFD0.png)

### Level 1 – System Decomposition
The Level 1 DFD decomposes the single system process into the main internal sub-processes.

In this project, the main sub-processes are:

- `1.0 Manage Patient Data`
- `2.0 Manage Appointments`
- `3.0 Search and View Information`

The logical data stores are:

- `D1 Patient Records`
- `D2 Appointment Records`

This level shows:

- how patient profile data enters the system
- how appointment requests are processed
- how patient and appointment data are stored and retrieved
- how the search/view process reads records from both data stores

Current diagram file:

- `src/Diagrams/DFD1.png`

Diagram preview:

![DFD Level 1](src/Diagrams/DFD1.png)

### Level 2 – Detailed View of Appointment Creation
The Level 2 view focuses on a specific core process instead of the entire system. In this project, the chosen detailed process is `Appointment Creation Flow`.

Although this level is presented as a DFD decomposition in the slides, it is technically closer to a sequence-style interaction flow. This is acceptable for the project because it explains one of the most important backend operations in detail.

The flow includes:

- `Patient`
- `AppointmentController`
- `AppointmentService`
- `PatientRepository`
- `AppointmentRepository`
- `Database`

Main steps:

1. The patient sends a request to create an appointment.
2. The controller forwards the request to the service layer.
3. The service validates the patient by checking `patientId`.
4. If the patient exists, the appointment is associated with that patient and saved.
5. The system returns `HTTP 201 Created`.
6. If the patient does not exist, the system returns `HTTP 404 Not Found`.

This level is useful because it shows one of the system’s most relevant internal operations with real backend components and data persistence behavior.

At the moment, no exported Level 2 diagram file was found in `src/Diagrams`. If the Level 2 image is later exported to that folder, it should also be referenced here.

## Threat Modeling

### Approach
This project uses **LINDDUN** as the threat modeling methodology.

LINDDUN was selected because it is more appropriate for systems that process:

- directly identifiable personal data
- sensitive appointment-related information
- data that may reveal health-related patterns

In this application, the system stores and processes:

- patient name
- email
- phone number
- date of birth
- appointment date and time
- specialty
- appointment status

Because of this, the main concern is not only traditional security, but also the **privacy impact** caused by identification, linkage of records, exposure of sensitive information, and the possibility of inferring personal or health-related patterns. For that reason, LINDDUN was considered the most suitable model for this analysis.

### LINDDUN Analysis

The following categories were analysed according to their relevance to the current project baseline and to the type of personal data handled by the application.

| LINDDUN Category | Relevance | Description |
| --- | --- | --- |
| Identifiability | High | The system stores direct personal identifiers such as name, email, phone number, and date of birth. This means a patient can be directly recognized from stored records, and any exposed appointment information can be associated with a real person. |
| Linkability | High | Patient identity data can be associated with appointment records through `patient_id` and related returned records. Once records are linked, an attacker may infer sensitive patterns such as appointment history, recurring specialties, visit frequency, and possible health-related conditions. |
| Disclosure of Information | High | Unauthorized access to patient or appointment endpoints may expose direct personal information, appointment date and time, specialty, and appointment status. This creates a significant privacy risk because personal identity and appointment context may both be revealed. |
| Detectability | Low / Medium | An attacker may determine whether a patient or appointment record exists by observing system responses to record lookups, searches, or identifier-based requests. This is weaker than the previous categories, but it may still leak the existence of sensitive records. |
| Non-repudiation | Low | This becomes relevant if patient actions such as creating, updating, or canceling appointments are strongly tied to a specific identity through stored logs or audit trails. In the current baseline, this risk is less explicit than the previous ones. |
| Unawareness | Medium | Patients may not be fully aware of what data is collected, how it is stored, how it is used, or what information may be exposed. This reduces transparency and informed understanding. |
| Non-compliance | Low / Medium | If directly identifiable and appointment-related data is processed without sufficient privacy controls, transparency, or clear handling practices, the system may create compliance risks related to privacy and data protection principles. |

Among the analysed categories, the most relevant ones for this project are:

- **Identifiability**
- **Linkability**
- **Disclosure of Information**

These three categories are the strongest because the application handles direct patient identifiers and links them to appointment records, making it possible to identify individuals, correlate their records, and expose sensitive appointment-related information.

## Attack Trees
Attack Trees were used to break down high-level attacker goals into concrete attack paths.

The current strongest root goal is:

- `Access Sensitive Patient Information`

This root goal can be reached through paths such as:

- calling patient endpoints directly
- calling appointment endpoints and inferring patient data
- enumerating patient or appointment identifiers
- using search and filter features to obtain records

Current attack tree file:

- `src/Diagrams/atta.png`

Diagram preview:

![Attack Tree](src/Diagrams/atta.png)

## Abuse Stories
Only this section should remain in the main software repository.

| ID | Title | Abuse case | How the abuse works | Impact |
| --- | --- | --- | --- | --- |
| AS-01 | Unauthorized Access to Patient Data | As a malicious external user, I want to access another patient's personal data so that I can obtain sensitive information such as name, email, phone number, date of birth, and linked appointment data. | The attacker sends direct requests to patient and appointment endpoints and retrieves records without sufficient access control. | Exposure of personal and appointment-related data, leading to a privacy breach. |
| AS-02 | Link Patient Identity to Appointment History | As a malicious external user, I want to associate patient identity data with appointment records so that I can infer sensitive patterns such as appointment history, recurring specialties, and possible health-related conditions. | The attacker correlates patient data with appointment records through linked identifiers and returned records. | Sensitive patterns can be inferred, increasing patient profiling risk. |
| AS-03 | Directly Identify a Patient from Stored Records | As a malicious external user, I want to use personal identifiers stored in the system so that I can directly identify a patient and associate exposed appointment information with a real individual. | The attacker accesses records containing direct identifiers such as name, email, phone number, and date of birth. | A real individual can be directly identified, increasing the severity of data exposure. |
| AS-04 | Create Fake Appointments for a Valid Patient | As a malicious external user, I want to create appointments using another patient's identifier so that I can introduce false records and disrupt the appointment management process. | The attacker submits appointment requests using a valid patient identifier and fabricated data. | False appointments may be created, damaging scheduling integrity. |
| AS-05 | Modify Another Patient's Appointment | As a malicious external user, I want to change the date, status, specialty, or linked patient of an appointment so that I can manipulate legitimate scheduling information. | The attacker sends unauthorized update requests to the appointment endpoints. | Legitimate scheduling data may be altered, affecting integrity and reliability. |
| AS-06 | Delete Valid Patient or Appointment Records | As a malicious external user, I want to remove patient or appointment records so that I can cause data loss and disrupt normal system operation. | The attacker invokes delete operations directly against exposed endpoints. | Valid records may be lost, disrupting normal system use. |
| AS-07 | Enumerate Valid Records Through Predictable Identifiers | As a malicious external user, I want to test patient and appointment identifiers so that I can discover which records exist and use them to gather or manipulate data. | The attacker probes predictable identifiers and observes which requests return valid records. | Valid targets can be discovered, enabling further attacks. |
| AS-08 | Overload the API with Repeated Requests | As an attacker, I want to flood patient and appointment endpoints with repeated requests so that I can make the system slow or unavailable for legitimate users. | The attacker automates repeated API requests until performance degrades. | The system may become slow or unavailable for normal users. |

## Final Notes
For this project, the most relevant privacy threats are:

- Identifiability
- Linkability
- Disclosure of Information

LINDDUN was used as the only threat modeling approach because it is more suitable for applications that process sensitive personal data. In this case, the system handles directly identifiable patient information and appointment-related data that may reveal sensitive patterns, making privacy-focused analysis the most appropriate choice.

The selected DFDs, LINDDUN analysis, attack tree, and abuse stories reflect the current project baseline and are aligned with the actual application structure: React frontend, Spring Boot backend, and PostgreSQL persistence.
