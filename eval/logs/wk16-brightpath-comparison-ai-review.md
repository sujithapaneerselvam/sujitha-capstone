# Week 16 — BrightPath graph comparison

Same 20 questions, memory ON in both runs.

## Week 15 raw agent

- Router model(s): gpt-5-mini
- Successful policy calls: 20/20 attempted
- Questions with no policy call: none
- Median latency: 9,942.5 ms
- Actual API cost: unmeasured

## Week 16 graph

- Router model(s): gpt-5-mini
- Successful policy calls: 19/19 attempted
- Questions with no policy call: q17
- Median latency: 15,397.0 ms
- Actual API cost: unmeasured

## q01: How many days of paid annual leave does an eligible employee receive for a complete calendar year?

**Reference:** 20 days of paid annual leave per complete calendar year

**Expected source(s):** ['HR_02_Annual_Leave_Policy.txt']

**Week 15:** - Eligible employees receive twenty (20) days of paid annual leave for each complete calendar year.  
  Source: HR_02_Annual_Leave_Policy.txt.

**Week 16:** - An eligible employee receives 20 days of paid annual leave for each complete calendar year.  
  Source: HR_02_Annual_Leave_Policy.txt [kb_version: v2.w10]

**Week 16 review:** Factual correctness: Yes. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: HR_02:23 confirms 20 days of paid annual leave per complete calendar year.

## q02: How far in advance should an employee request three or more consecutive days of annual leave?

**Reference:** A request for three or more consecutive days of annual leave should be submitted at least 10 working days in advance.

**Expected source(s):** ['HR_02_Annual_Leave_Policy.txt']

**Week 15:** - Employees must submit requests for three or more consecutive days of annual leave at least ten working days in advance. (HR_02_Annual_Leave_Policy.txt)

**Week 16:** - Employees must submit requests for three or more consecutive days of annual leave at least ten working days in advance (HR_02_Annual_Leave_Policy.txt).

**Week 16 review:** Factual correctness: Yes. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: HR_02:25 requires at least ten working days of notice for three or more consecutive days.

## q03: What are the standard collaboration hours for an employee working remotely?

**Reference:** The standard remote-work collaboration hours are 10:00 a.m. to 4:00 p.m. IST.

**Expected source(s):** ['HR_03_Remote_Work_Policy.txt']

**Week 15:** - Standard collaboration hours for remote employees: 10:00 a.m. to 4:00 p.m. IST. (Source: HR_03_Remote_Work_Policy.txt; also referenced in HR_01_Employee_Onboarding_Guide.txt)

**Week 16:** - Standard collaboration hours for remote employees: 10:00 a.m. to 4:00 p.m. IST. (Source: HR_03_Remote_Work_Policy.txt)  
- Also referenced in: HR_01_Employee_Onboarding_Guide.txt.

**Week 16 review:** Factual correctness: Yes. Corpus grounding: Yes. Citation validity: No. Bullet preference: Yes. Evidence: HR_03:25 supports 10:00 a.m. to 4:00 p.m. IST. The additional HR_01 citation concerns first-day orientation, not recurring collaboration hours.

## q04: Which family members can an employee register as dependants under the medical plan?

**Reference:** Eligible dependants include a spouse or declared partner, up to two dependent children, and either the employee's parents or parents-in-law.

**Expected source(s):** ['HR_04_Employee_Benefits_Guide.txt']

**Week 15:** - Spouse or declared partner  
- Up to two dependent children  
- Either parents or parents-in-law

Source: HR_04_Employee_Benefits_Guide.txt [1]

**Week 16:** - Spouse or declared partner (HR_04_Employee_Benefits_Guide.txt)  
- Up to two dependent children (HR_04_Employee_Benefits_Guide.txt)  
- Either parents or parents‑in‑law (HR_04_Employee_Benefits_Guide.txt)

**Week 16 review:** Factual correctness: Yes. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: HR_04:23 supports all three dependant groups, the two-child limit, and the choice of parents or parents-in-law.

## q05: Which flight class should normally be booked for a business flight lasting less than six hours?

**Reference:** Economy class should normally be booked for a business flight lasting less than six hours.

**Expected source(s):** ['HR_05_Travel_and_Expense_Policy.txt']

**Week 15:** - Economy class should normally be booked for business flights lasting less than six hours (HR_05_Travel_and_Expense_Policy.txt)

**Week 16:** - Economy class — HR_05_Travel_and_Expense_Policy.txt: “Economy class should normally be booked for a business flight lasting less than six hours.” [HR_05_Travel_and_Expense_Policy.txt]

**Week 16 review:** Factual correctness: Yes. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: HR_05:25 supports economy class for business flights under six hours.

## q06: What is the minimum required length for a BrightPath corporate password?

**Reference:** The length of the password must contain at least 14 characters

**Expected source(s):** ['IT_01_Password_and_MFA_Guide.txt']

**Week 15:** - Minimum required length: at least 14 characters. (Source: IT_01_Password_and_MFA_Guide.txt, kb_version v2.w10)

**Week 16:** - Minimum required length: at least fourteen characters (source: IT_01_Password_and_MFA_Guide.txt).

**Week 16 review:** Factual correctness: Yes. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: IT_01:23 sets the minimum corporate password length at fourteen characters.

## q07: From where should an employee download the approved corporate VPN client?

**Reference:** Employees can download the VPN client from the corporate software centre

**Expected source(s):** ['IT_02_VPN_Setup_Guide.txt']

**Week 15:** - Download location: the corporate software centre. (Source: IT_02_VPN_Setup_Guide.txt)  
- Prohibited sources: search results, personal storage, or unverified websites. (Sources: IT_02_VPN_Setup_Guide.txt; HR_03_Remote_Work_Policy.txt)

**Week 16:** - Download the approved corporate VPN client from the corporate software centre.  
  - Downloads from search results, personal storage, or unverified websites are prohibited.  

Sources:
- IT_02_VPN_Setup_Guide.txt [1]
- HR_03_Remote_Work_Policy.txt [1]

**Week 16 review:** Factual correctness: Yes. Corpus grounding: Yes. Citation validity: No. Bullet preference: Yes. Evidence: IT_02:24 supports the corporate software centre and download restrictions. HR_03 does not establish the download source; both files are labelled [1].

## q08: Who should an employee contact first after discovering that a company laptop is missing?

**Reference:** The first contact for a missing laptop is the security hotline. Emergency services apply only when there is danger or theft in progress

**Expected source(s):** ['IT_06_Lost_or_Stolen_Device_Procedure.txt']

**Week 15:** - Contact your manager immediately. (Source: HR_01_Employee_Onboarding_Guide.txt)
- Contact the IT service desk immediately. (Source: IT_06_Lost_or_Stolen_Device_Procedure.txt)

Sources: HR_01_Employee_Onboarding_Guide.txt; IT_06_Lost_or_Stolen_Device_Procedure.txt; IT_03_Laptop_and_Equipment_Policy.txt

**Week 16:** - Contact your manager immediately.
- Contact the IT service desk immediately.

Source(s): HR_01_Employee_Onboarding_Guide.txt; IT_06_Lost_or_Stolen_Device_Procedure.txt; IT_03_Laptop_and_Equipment_Policy.txt.

**Week 16 review:** Factual correctness: No. Corpus grounding: No. Citation validity: No. Bullet preference: Yes. Evidence: IT_06_Lost_or_Stolen_Device_Procedure.txt, line 52, explicitly names the security hotline as the first contact. The answer cites that document but tells the employee to contact the manager and IT service desk instead.

## q09: What account-security and remote-access activities should a new remote employee complete on the first day?

**Reference:** On the first day, the employee should activate the corporate account, register MFA, confirm receipt of the equipment, install the approved VPN client, and verify that the VPN connection works using the corporate credentials and MFA.

**Expected source(s):** ['HR_01_Employee_Onboarding_Guide.txt', 'IT_01_Password_and_MFA_Guide.txt', 'IT_02_VPN_Setup_Guide.txt']

**Week 15:** - Status: I cannot verify any account-security or remote-access activities for a new remote employee on the first day. The policy lookup returned: "The provided context does not specify any account-security and remote-access activities that a new remote employee should complete on the first day."  
  - Source: HR_01_Employee_Onboarding_Guide.txt (kb_version: v2.w10)

- Next steps you can request (I can run these lookups):  
  - Search the onboarding guide for terms like "first day", "security checklist", "remote access", or "IT setup".  
  - Check the IT/Access policy or New Hire IT checklist specifically.  
  - Ask HR/IT directly for the first-day security checklist if you need it immediately (I cannot contact them for you).

**Week 16:** - Summary: I cannot verify any BrightPath policy that lists account-security or remote-access activities a new remote employee must complete on their first day.  
  - Source returned: HR_01_Employee_Onboarding_Guide.txt (kb_version: v2.w10). The lookup result indicates the guide does not specify those activities. [lookup_policy result]
- Next steps you can ask me to do:
  - Retry the policy lookup with a more specific query (examples: "first-day IT checklist", "VPN enrollment for new hires", "multi-factor authentication setup new employee").  
  - Search other policy documents (IT security, remote-work, or onboarding subguides) if you want me to look for related instructions.  

If you want me to retry, tell me which specific terms or documents to search.

**Week 16 review:** Factual correctness: No. Corpus grounding: No. Citation validity: No. Bullet preference: Yes. Evidence: HR_01_Employee_Onboarding_Guide.txt, line 35, explicitly requires account activation, MFA registration, and equipment confirmation on day one. The answer cites this guide while saying it does not specify those activities.

## q10: What precautions should an employee take before accessing internal services from public Wi-Fi?

**Reference:** Public WIFI should be treated as untrusted,hence before connecting verify the network name and disable automatic connection and also connect to VPN to access the internal resources with an approved managed device and MFA

**Expected source(s):** ['HR_03_Remote_Work_Policy.txt', 'IT_01_Password_and_MFA_Guide.txt', 'IT_02_VPN_Setup_Guide.txt']

**Week 15:** - Verify the network name before connecting. (Source: IT_02_VPN_Setup_Guide.txt)  
- Disable automatic connection to networks. (Source: IT_03_Laptop_and_Equipment_Policy.txt)  
- Start the corporate VPN before opening any internal resources. (Source: IT_02_VPN_Setup_Guide.txt)  
- Make sure personal proxy tools, consumer VPN products, or other network‑bypass utilities are not running alongside the corporate VPN client. (Source: IT_02_VPN_Setup_Guide.txt)

**Week 16:** From policy, before accessing internal services from a public <LOCATION> take these precautions:

- Verify the network name.  
- Disable automatic connection to networks.  
- Start the VPN before opening internal resources.  
- Ensure that split tunnelling is not changed, as it is centrally configured.  
- Avoid running personal proxy tools, consumer VPN products, and network-bypass utilities alongside the corporate client.

Sources:
- IT_02_VPN_Setup_Guide.txt  
- IT_03_Laptop_and_Equipment_Policy.txt  
- IT_02_VPN_Setup_Guide.txt (kb_version: v2.w10)

**Week 16 review:** Factual correctness: No. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: IT_02:27–28 supports the network precautions given. The answer omits the managed-device and MFA requirements in IT_02:23–25.

## q11: What should an employee do if a phone containing the corporate authenticator application is lost?

**Reference:** The employee should immediately report the loss through the security hotline, change the corporate password from a trusted device, deny unexpected MFA prompts, and ask the service desk to revoke the old authenticator before enrolling the replacement device.

**Expected source(s):** ['IT_01_Password_and_MFA_Guide.txt', 'IT_05_Incident_Reporting_Procedure.txt', 'IT_06_Lost_or_Stolen_Device_Procedure.txt']

**Week 15:** - Report the loss immediately. [IT_01_Password_and_MFA_Guide.txt; IT_06_Lost_or_Stolen_Device_Procedure.txt]
- Have Security revoke the old MFA registration before enrolling a replacement phone to mitigate account risk. [IT_01_Password_and_MFA_Guide.txt]

**Week 16:** - Report the loss immediately so the security team can respond. (IT_01_Password_and_MFA_Guide.txt)
- The security team will revoke the old MFA/authenticator registration before you enroll a replacement phone to mitigate account risk. (IT_01_Password_and_MFA_Guide.txt; IT_06_Lost_or_Stolen_Device_Procedure.txt)

**Week 16 review:** Factual correctness: No. Corpus grounding: No. Citation validity: No. Bullet preference: Yes. Evidence: IT_06:25–26 and 35–36 specify the hotline, a trusted-device password change, and denial of unexpected MFA prompts. IT_01:48 identifies the service desk for authenticator revocation; the answer assigns that action to the security team.

## q12: What steps and approvals are required to provide a new employee with access to a business application?

**Reference:** The hiring manager submits the access request with the business reason and required permission. The reporting manager approves the business need, and the application owner approves the appropriate permission level. The lowest level of access needed for the work should be granted.

**Expected source(s):** ['HR_01_Employee_Onboarding_Guide.txt', 'IT_04_Software_Access_Request_Process.txt']

**Week 15:** - Manager confirms the business need for the new employee’s access. [IT_04_Software_Access_Request_Process.txt]  
- Manager submits the access request and identifies the intended user and required start date. [IT_04_Software_Access_Request_Process.txt]  
- The new employee is responsible for reading the relevant requirements and providing accurate information as needed. [HR_01_Employee_Onboarding_Guide.txt]  
- The request must go through the necessary approvals as outlined in the access request process. [IT_04_Software_Access_Request_Process.txt]  
- Access must be tied to a named user with a legitimate business need; shared accounts are prohibited unless a documented exception is made by the application owner. [IT_04_Software_Access_Request_Process.txt]

**Week 16:** - Manager confirms there is a legitimate business need for the new employee to have the application access. (IT_04_Software_Access_Request_Process.txt)  
- Manager submits an access request that identifies the intended user and the required start date. (IT_04_Software_Access_Request_Process.txt; HR_01_Employee_Onboarding_Guide.txt)  
- New employee must read the relevant requirements and provide accurate information as requested. (HR_01_Employee_Onboarding_Guide.txt)  
- The access request must go through the required approval steps as outlined in the access request process. (IT_04_Software_Access_Request_Process.txt)  
- Access must be assigned to a named user and tied to a legitimate business need; shared accounts are prohibited unless a documented exception is approved by the application owner. (IT_04_Software_Access_Request_Process.txt)

Sources:
- IT_04_Software_Access_Request_Process.txt  
- HR_01_Employee_Onboarding_Guide.txt

**Week 16 review:** Factual correctness: No. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: IT_04:23–27 and HR_01:25 support the request and business-need details. The answer omits application-owner approval of the permission level and the least-privilege rule.

## q13: How should an employee protect a company laptop and internal access while travelling for business?

**Reference:** The employee should use a company-managed device, verify the public network name, disable automatic connection, and connect to the corporate VPN before opening internal resources. The device should remain screen-locked and must not be left unattended in public places or vehicles.

**Expected source(s):** ['HR_03_Remote_Work_Policy.txt', 'HR_05_Travel_and_Expense_Policy.txt', 'IT_02_VPN_Setup_Guide.txt', 'IT_03_Laptop_and_Equipment_Policy.txt']

**Week 15:** - Permit automatic security updates on the company laptop so it stays patched and secure. (IT_03_Laptop_and_Equipment_Policy.txt)  
- Use a screen lock whenever the device is unattended to prevent unauthorized access. (IT_03_Laptop_and_Equipment_Policy.txt)  
- Protect the device from unauthorized physical access—do not leave it unattended in public places or in vehicles. (IT_03_Laptop_and_Equipment_Policy.txt)  
- Do not let family members or other unauthorized people use company equipment, even for brief personal tasks. (IT_03_Laptop_and_Equipment_Policy.txt)  
- If the device is lost or stolen, follow the Lost or Stolen Device Procedure. (IT_06_Lost_or_Stolen_Device_Procedure.txt)

**Week 16:** - Permit automatic security updates on the company laptop. (Source: IT_03_Laptop_and_Equipment_Policy.txt)  
- Use a screen lock whenever the device is unattended. (Source: IT_03_Laptop_and_Equipment_Policy.txt)  
- Protect the device from unauthorized access; do not allow family members or other unauthorized people to use company equipment, even briefly. (Source: IT_03_Laptop_and_Equipment_Policy.txt)  
- Do not leave company equipment unattended in public places or in vehicles. (Source: IT_03_Laptop_and_Equipment_Policy.txt; IT_06_Lost_or_Stolen_Device_Procedure.txt)

**Week 16 review:** Factual correctness: No. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: IT_03:25–26 supports the device protections given. The answer omits public-network checks and the requirement in IT_02:27 to connect the VPN before opening internal resources.

## q14: What should an employee do if they become medically unfit during approved annual leave while travelling?

**Reference:** If an employee becomes medically unfit during annual leave, they may request that the absence be reclassified as sick leave by submitting acceptable medical evidence within three working days after returning. For an emergency while travelling, the employee should use local emergency services and notify the travel provider and manager.

**Expected source(s):** ['HR_02_Annual_Leave_Policy.txt', 'HR_05_Travel_and_Expense_Policy.txt']

**Week 15:** - Request that the period be reclassified from annual leave to sick leave.  
- Provide acceptable medical evidence within three working days of returning to work.  

Source: HR_02_Annual_Leave_Policy.txt.

**Week 16:** - You may request that the period be reclassified from annual leave to sick leave.  
- Provide acceptable medical evidence within three working days of returning to work.  
  - Source: HR_02_Annual_Leave_Policy.txt [1]

**Week 16 review:** Factual correctness: Yes. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: HR_02:30 supports reclassification as sick leave and the three-working-day evidence deadline. Emergency escalation is conditional; the question describes illness but does not say it is an emergency.

## q15: When a remote employee leaves the company, what should happen to assigned equipment and unnecessary application access?

**Reference:** All the assigned equipment should be returned by the date specified for separation and data should not be copied in personal storage before return. The manager ensures unnecessary access is removed.

**Expected source(s):** ['IT_03_Laptop_and_Equipment_Policy.txt', 'IT_04_Software_Access_Request_Process.txt']

**Week 15:** - Assigned equipment: the employee keeps the equipment until Asset Management records its receipt — after the employee follows the approved packaging and courier instructions. (Source: IT_03_Laptop_and_Equipment_Policy.txt)

- Unnecessary application access: remove through the transfer/separation workflow managed by the employee’s manager. (Source: IT_04_Software_Access_Request_Process.txt)

**Week 16:** - Assigned equipment: remains with the remote employee until Asset Management records receipt — Asset Management will provide approved packaging and courier instructions. (Source: IT_03_Laptop_and_Equipment_Policy.txt)

- Unnecessary application access: must be removed via the transfer/separation workflow and handled by the manager. (Sources: IT_04_Software_Access_Request_Process.txt; IT_03_Laptop_and_Equipment_Policy.txt)

**Week 16 review:** Factual correctness: No. Corpus grounding: No. Citation validity: No. Bullet preference: Yes. Evidence: IT_03:30 and 48 distinguish returning equipment by the deadline from remaining administratively assigned until receipt. The answer says the equipment remains with the employee. IT_04:30 supports the separate access-removal claim.

## q16: What should an employee do if a software supplier offers a shopping voucher while the employee is involved in selecting the supplier?

**Reference:** The voucher must be declined and reported, especially because supplier selection is active.

**Expected source(s):** ['HR_06_Code_of_Conduct.txt', 'IT_04_Software_Access_Request_Process.txt']

**Week 15:** - Decline the shopping voucher.  
- Report the offer — the policy says it “creates an unacceptable appearance of influence” while you are involved in selecting the supplier, so you must report it.  

Source: HR_06_Code_of_Conduct.txt [1].

**Week 16:** - Decline the shopping voucher.
- Report the offer (it creates an unacceptable appearance of influence while you are involved in selecting the supplier).

Source: HR_06_Code_of_Conduct.txt [policy lookup].

**Week 16 review:** Factual correctness: Yes. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: HR_06 supports declining and reporting a voucher during supplier selection. The answer gives both actions.

## q17: What is the exact rupee limit for meals during a business trip to Chennai?

**Reference:** The exact Chennai meal limit is not specified in the available corpus. The employee should check the currently published city limit or contact Finance Help.

**Expected source(s):** []

**Week 15:** - I cannot verify the exact rupee limit for meals during a business trip to Chennai from the available BrightPath policy documents.  
  - Lookup result: "The provided context does not specify the exact rupee limit for meals during a business trip to Chennai." (source: HR_05_Travel_and_Expense_Policy.txt; kb_version: v2.w10)

- Suggested next steps:
  - Check HR_05_Travel_and_Expense_Policy.txt on the company policy portal or your shared policy drive (the policy file returned no meal-amount detail in the lookup).  
  - If you need a definitive number now, ask HR or the Travel Desk for the current per-meal/per-day allowance for Chennai, and provide your travel dates and job grade if applicable.

**Week 16:** - I don’t have a specific location to look up — please tell me the exact city/country (or region) for "<LOCATION>" so I can fetch the policy.  
- If the allowance depends on job level (e.g., manager vs. individual contributor) or trip type (domestic vs. international), please say which applies.  
- If the trip date matters (policy changed recently), tell me the travel dates or effective date you need.  

Once you provide that, I will look up the exact rupee meal limit and include the policy citation.

**Week 16 review:** Factual correctness: No (incomplete). Corpus grounding: N/A (clarification only). Citation validity: N/A (no policy claim cited). Bullet preference: Yes. Evidence: The question already named Chennai. The answer avoided inventing a rupee amount but asked for the city again and promised an exact figure it had not verified. HR_05_Travel_and_Expense_Policy.txt, line 27, refers to the published city limit; line 52 directs policy interpretation questions to Finance Help. No tool call was attempted.

## q18: For exactly how many days may an employee work from outside India without additional approval?

**Reference:** The policy does not specify a maximum number of approved international remote-working days. The employee should contact People Operations for case-specific confirmation.

**Expected source(s):** []

**Week 15:** - Short answer: The policy does not specify any exact number of days an employee may work from outside India without additional approval. It states that working from outside India is not automatically permitted and requires approvals before travel.
- Evidence: lookup returned no specific allowance and noted approvals are required (HR_03_Remote_Work_Policy.txt).  
  - Sources returned: HR_03_Remote_Work_Policy.txt (score: 6.50), HR_03_Remote_Work_Policy.txt (score: 5.87), HR_01_Employee_Onboarding_Guide.txt (score: 0.38).

**Week 16:** - I cannot verify an exact number of days from the policy text returned — the policy does not specify a specific number of days an employee may work from outside <LOCATION> without additional approval. (HR_03_Remote_Work_Policy.txt)  
- The policy indicates working from outside India (and similar cases) is not automatically permitted and requires approvals, but no clear day limit is given in the retrieved policy text. (HR_03_Remote_Work_Policy.txt)  
- Sources checked: HR_03_Remote_Work_Policy.txt; no definitive day-count found.

**Week 16 review:** Factual correctness: Yes. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: HR_03:28–29 distinguishes domestic relocation from international work requiring prior approval. No international day allowance is specified. The answer correctly declines to give a number; a People Operations referral would improve it.

## q19: How much must an employee pay to replace a company laptop that was accidentally damaged?

**Reference:** The policy does not specify how much an employee must pay for accidental laptop damage. The employee should report the damage to IT Asset Management or the IT service desk for assessment.

**Expected source(s):** []

**Week 15:** - I cannot verify an exact dollar amount from BrightPath policy: the policy text searched (IT_03_Laptop_and_Equipment_Policy.txt) does not specify how much an employee must pay to replace an accidentally damaged company laptop (lookup returned no replacement-cost amount). Source: IT_03_Laptop_and_Equipment_Policy.txt.  
  
- Recommended next steps (to get the definitive answer):  
  - Review the IT_03_Laptop_and_Equipment_Policy.txt (company policy library) yourself for any nearby sections about liability or asset replacement.  
  - Contact your HR or IT asset manager or your manager to request the specific replacement fee and the official replacement process.  

Citation: IT_03_Laptop_and_Equipment_Policy.txt (policy search returned no specified replacement cost).

**Week 16:** - I cannot verify from the current BrightPath policy how much an employee must pay to replace a company laptop that was accidentally damaged.  
  - Evidence: lookup returned "The provided context does not specify..."  
  - Source: IT_03_Laptop_and_Equipment_Policy.txt (kb_version: v2.w10)  

- Would you like me to:
  - search for related policies (e.g., equipment, IT, or reimbursements) or
  - suggest who to contact at BrightPath to get an official answer?

**Week 16 review:** Factual correctness: Yes. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: IT_03:29 and 47 require prompt damage reporting and a repair ticket but give no replacement fee. The answer correctly declines to invent an amount; it could name the reporting contact directly.

## q20: What is the exact maximum medical insurance coverage amount available to each employee?

**Reference:** As per the policy document the medical coverage limit is not mentioned anywhere ,hence please refer to the Benefits portal or Total Rewards team.

**Expected source(s):** []

**Week 15:** - I cannot verify the exact maximum medical insurance coverage amount from the available policy documents.
  - Source searched: HR_04_Employee_Benefits_Guide.txt (lookup returned no specific amount). [kb_version: v2.w10]
- Suggested next steps you can take to get the exact amount:
  - Check the BrightPath benefits portal or the full employee benefits guide PDF.
  - Contact HR/Benefits directly to request the precise maximum coverage figure.

**Week 16:** - I cannot verify the exact maximum medical insurance coverage amount from BrightPath policies based on the available documents. The lookup returned: "The provided context does not specify the exact maximum medical insurance coverage amount available to each employee."
- Source(s) returned by the policy lookup:
  - HR_04_Employee_Benefits_Guide.txt (kb_version: v2.w10)
- Suggested next steps:
  - Check the latest Employee Benefits Guide or the Benefits section on the employee portal, or
  - Contact your HR/Benefits team for the exact maximum coverage amount.

**Week 16 review:** Factual correctness: Yes. Corpus grounding: Yes. Citation validity: Yes. Bullet preference: Yes. Evidence: HR_04:30 and 34 direct employees to current benefits information in the portal. The answer gives no unsupported maximum and points to Benefits.
