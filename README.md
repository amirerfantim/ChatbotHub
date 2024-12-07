### Torob Chatbot: AI-Powered Customer Support Solution 🚀

The **Torob Chatbot** is an innovative AI-powered project designed to revolutionize customer interactions for businesses. Leveraging cutting-edge natural language processing (NLP) technologies such as OpenAI's GPT models, it provides a robust platform built with Django to handle real-time customer inquiries. This project empowers businesses to deliver personalized responses while dynamically managing content, reducing operational costs, and enhancing user satisfaction.

---

## 🌟 Key Highlights

### 🎯 Purpose
- **Improve Customer Experience:** Provide instant responses to user queries, enhancing satisfaction and engagement.
- **Reduce Costs:** Minimize reliance on human operators through intelligent automation.
- **Enable Customization:** Allow businesses to build and manage tailored chatbots with unique knowledge bases.

### ⚡ Core Functionalities
- **Dynamic Knowledge Base:** Define and upload knowledge bases to customize chatbot responses.
- **Real-Time AI:** Handle diverse user inquiries with OpenAI-powered conversational capabilities.
- **Advanced Search:** Use similarity search with vector embeddings for precise and contextually relevant answers.
- **Comprehensive Admin Tools:** Monitor, edit, and manage chatbot behaviors, configurations, and feedback.

### 🌈 Innovative Features
- **Retrieval-Augmented Generation (RAG):** Combines retrieval-based techniques with generative AI for accurate responses.
- **Dynamic Updates:** Modify chatbot prompts and settings in real-time.
- **Search Capabilities:** Perform full-text searches within historical conversations.
- **Feedback Mechanisms:** Use like/dislike buttons to improve chatbot responses and refine future interactions.

---

## 🛠️ Features  

### 🔑 User Roles  
- **👤 General User:** Interact with chatbots for inquiries and support.  
- **👨‍💻 Chatbot Creator:** Build, customize, and manage chatbot knowledge bases.  
- **🛡️ Admin:** Oversee all chatbots, modify configurations, and manage global settings.  

### 🤖 Chatbot Capabilities  
- **Customizable Chatbots:** Create chatbots with unique names, prompts, and settings.  
- **State Management:** Activate or deactivate chatbots as needed.  
- **Dynamic Responses:** Use defined knowledge bases for precise query handling.  
- **Vector Search Integration:** Enhance response matching with semantic vector embeddings.  

### 💬 Conversation Management  
- Start new or continue existing conversations with selected chatbots.  
- Search and access historical conversation logs for insights and references.  
- Provide feedback on responses to refine system performance.  

### 📚 Dynamic Content Management  
- Add, edit, or delete chatbot content dynamically through user-friendly tools.  
- Maintain quality by enforcing content length limits (e.g., 800-character maximum).  

### 📈 Feedback Integration  
- Enable users to like or dislike responses, triggering regeneration for improved accuracy.  
- Use feedback to refine the overall performance and relevance of responses.  

---

## 🏗️ Project Structure  

```
torob-chatbot/
├── torob_chatbot/            # Main project folder
│   ├── requirements.txt      # Python dependencies
│   ├── templates/            # HTML templates for the web interface
│   ├── Dockerfile            # Docker configuration for containerization
│   ├── manage.py             # Django project management
│   ├── content-adder.py      # Script for dynamic dataset updates
│   ├── test-dataset.py       # Script for validating dataset quality
│   ├── chatbot/              # Core chatbot logic
│   ├── data/                 # Data directory (e.g., datasets, configurations)
│   ├── dataset_result/       # Directory for processed datasets
│   └── ...                   # Additional project files and modules
├── .gitlab-ci.yml            # GitLab CI/CD pipeline configuration
├── Torob-Blogpost.pdf        # Additional project documentation
└── README.md                 # Documentation (this file)
```

---

## ⚙️ Technical Details  

### 🌟 Core Technologies  
- **🛠️ Django:** Backend framework for the web interface and APIs.  
- **🐘 PostgreSQL:** Database management system with `pgvector` for semantic search.  
- **🤖 OpenAI API:** Enables advanced conversational AI functionalities.  
- **🐳 Docker:** Provides a consistent, containerized runtime environment.  

### 🔍 Key Features  
- **Retrieval-Augmented Generation:** Combines generative AI with retrieval-based techniques for improved response accuracy.  
- **Feedback System:** Collects user feedback (like/dislike) to refine chatbot responses.  
- **Vector Search:** Uses embeddings to enhance relevance and precision in queries.  

---

## 🐳 Deployment with Docker  

1. **📦 Build the Docker Image:**  
   ```bash
   docker build -t torob-chatbot .
   ```  

2. **🚀 Run the Docker Container:**  
   ```bash
   docker run -p 8000:8000 -v /data torob-chatbot
   ```  

3. **🌐 Access the Application:**  
   Visit `http://localhost:8000` in your browser.  

---

## 🚀 Usage  

### 📂 Adding Content  
Use the `content-adder.py` script to add new data:  
```bash
python content-adder.py --file path_to_dataset.csv
```  

### 🧪 Testing Datasets  
Validate datasets for quality and performance:  
```bash
python test-dataset.py
```  

### 💬 Real-Time Interactions  
- Start conversations through the web interface.  
- Search historical conversations for insights.  
- Provide feedback to fine-tune chatbot responses.  

---

## 🙌 Authors and Acknowledgments  

- **Main Author:** Amirerfan Teimoori 👨‍💻  
- **Acknowledgments:** Torob Bootcamp 1402 team for guidance and mentorship. 🙏  
``
