# 🌙 Resilience Coach Agent — Updated UI/UX Improvement Specification  
### **Professional, Clean, Accessible Chat Interface (HTML/CSS/JS — No Frameworks)**  
### **Theme: Dark Blue + White, Minimalistic, Professional, Mental-Health Friendly**

---

## 🎯 **1. Overall Design Goals**
The updated UI must:
- Look **professional**, **clean**, and **minimalistic**
- Use **only HTML, CSS, JS** (no frameworks)
- Use a **dark-blue + white theme**, no gradients
- Maintain **high readability**, **calming visual tone**, and **proper spacing**
- Ensure **clear separation** between user messages and agent messages
- Provide a **structured layout** with visually balanced sections
- Feel appropriate for a **mental wellness AI agent**, with gentle wording and layout

---

## 🎨 **2. Color Palette (Simple, Professional)**
Use a **small set** of colors consistently:

| Element | Color |
|--------|--------|
| Header background | `#0C2340` (deep professional navy blue) |
| Page background | `#F4F7FA` (soft white/grey) |
| User message bubble | `#0C2340` (navy blue) |
| User message text | `#FFFFFF` (white) |
| Agent message bubble | `#FFFFFF` (white) |
| Agent message text | `#0C2340` (navy blue) |
| Border accents | `#D0D6E0` |
| Input box background | `#FFFFFF` |
| Input box text | `#0C2340` |
| Send button active | `#0C2340` |
| Send button disabled | `#AAB4C3` |

---

## 🧩 **3. Layout Improvements**
### **3.1 Header Section**
- Remove gradients completely  
- Use a **solid navy bar**
- Include:
  - **Project title** (Resilience Coach Agent)
  - **Subtitle** (AI-Powered Mental Wellness Support)
  - A **small status indicator dot** showing connection status  
- All centered and balanced  
- Add **vertical padding** to avoid cramped visuals  

### **3.2 Chat Container**
- Should be centered on the page with:
  - Max width: **600–650px**
  - Rounded corners: **12px**
  - White background
  - Light shadow for elevation

### **3.3 Message Area**
Enhance message clarity:
- User messages:
  - Right aligned  
  - Navy bubble, white text  
  - Rounded 15px radius  
- Agent messages:
  - Left aligned  
  - White bubble with navy border and navy text  
  - Rounded 15px radius  
- Maintain **consistent spacing** between messages  
- Add a **timestamp** (small, subtle grey)

---

## 🧠 **4. Typography Guidelines**
- Font: `Inter`, `Roboto`, `Segoe UI`, or system default  
- No decorative font styles  
- Text sizes:
  - Header title: **24–28px** bold
  - Subtitle: **14–16px**
  - Body content: **15–16px**
  - Message text: **15–16px**
  - Timestamp: **12px**

Use **consistent line-height (1.5–1.7)** for readability.

---

## 📱 **5. Input Area Improvements**
### Make the message input intuitive and clean:
- A **white input box** with navy text  
- Placeholder text in soft grey  
- Character counter below (0 / 2000)  
- Send button:
  - Navy when active  
  - Light grey when disabled  
  - Smooth hover transition  
- Add **proper padding** inside the textarea  

### Behavior:
- Automatically disable “Send” when the field is empty  
- Allow Enter to send message  
- Auto-expand the input area if needed  

---

## 💬 **6. Conversation Flow Enhancements**
### Additional UI Interaction Rules:
- After sending a message:
  - User message appears instantly
  - Agent message shows a **typing indicator** (3 pulsing dots)
- Scroll container auto-scrolls to the latest message  
- Recommended strategy responses should appear as:
  - A **boxed card** with yellow left border
  - Title in bold navy blue
  - Steps as a numbered list for clarity

---

## 🪟 **7. Cards for Recommendations**
When the agent sends coping strategies, structure them as:


### Visual Style:
- White background  
- Yellow left border: `#F2C94C`  
- Navy text  
- Slight shadow  

---

## 🧱 **8. Spacing & Alignment Rules**
To create a clean, breathable UI:
- Use **20–24px padding** inside containers  
- Add **16px margin** between messages  
- Add **top spacing** (at least 40px) before first content block  
- Stick to a **single-column layout**

---

## 🧭 **9. Accessibility Requirements**
- High contrast: Navy on white & white on navy  
- Large enough touch targets  
- Labels on input fields  
- Screen-reader-friendly text where needed  
- No flashing animations  
- Typing indicator must be subtle, low-motion  

---

## ☑️ **10. What Will This Improved UI Achieve?**
This redesigned UI will be:
- Calm and professional  
- Optimized for mental-health-related interactions  
- Easy to read and use  
- Lightweight and fast (pure HTML/CSS/JS)  
- Visually aligned with the Resilience Coach Agent theme  
- Perfectly suitable for your semester project presentation  

---

## 📄 **11. Delivery Expectations**
The final output should include:
- `index.html`
- `style.css`
- `script.js`
- Fully functional message flow  
- Improved design following all requirements in this `.md`  

---

## 👍 Final Note
This specification is ready for you to hand to a developer or Copilot to implement accurately.

If you want, I can also generate:
- The full code  
- A preview mockup  
- An interactive animation (typing indicator)  
- A dark-mode toggle  

Just tell me!
