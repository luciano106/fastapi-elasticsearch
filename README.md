# FastAPI + Elasticsearch API

This project is a REST service built with **FastAPI** and **Elasticsearch**, enabling operations on indexed data within Elasticsearch.

## 🚀 Features
- 📡 **RESTful API** with FastAPI
- 📦 **Elasticsearch support** as the main database
- 🐳 **Docker & Docker Compose** for easy deployment
- 🔄 **Multi-environment configuration**: `dev`, `qa`, `uat`, `prod`
- 🔥 **Supports local execution without Docker**

---

## 📂 Project Structure

```bash
fastapi-elasticsearch/
│── app/                   # Main application code
│   ├── main.py             # FastAPI entry point
│   ├── config.py           # Dynamic configuration per environment
│   ├── database.py         # Elasticsearch connection
│   ├── models.py           # Data models (Pydantic)
│   ├── routes.py           # API routes
│   ├── elastic_utils.py    # Helper functions for Elasticsearch
│── config/                 # Separate configurations per environment
│   ├── dev.env             # Development configuration
│   ├── qa.env              # QA configuration
│   ├── uat.env             # UAT configuration
│   ├── prod.env            # Production configuration
│── docker/                 # Environment-specific Dockerfiles
│   ├── Dockerfile.dev      # Development Dockerfile
│   ├── Dockerfile.qa       # QA Dockerfile
│   ├── Dockerfile.uat      # UAT Dockerfile
│   ├── Dockerfile.prod     # Production Dockerfile
│── docker-compose.yml      # Docker Compose setup
│── requirements.txt        # Project dependencies
│── .env                    # Environment variables for local execution
│── .env.example            # Reference file for configurations
│── README.md               # Project documentation
```

---

## 🔧 **Local Setup (Without Docker)**

### 1️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2️⃣ **Set Up Environment Variables**
```bash
cp .env.example .env
```
🔹 **Edit the `.env` file** with the necessary local configurations.

### 3️⃣ **Run the Application**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4️⃣ **Test the API**
Open in browser:
```
http://localhost:8000/docs
```

---

## 🐳 **Running with Docker**

### **1️⃣ Build and Start the Container**
```bash
docker-compose up --build
```

### **2️⃣ Start in Detached Mode**
```bash
docker-compose up -d
```

### **3️⃣ Stop the Containers**
```bash
docker-compose down
```

---

## 🌍 **Running in Different Environments (TBD)**

To run in a specific environment (`dev`, `qa`, `uat`, `prod`), define the `ENVIRONMENT` variable before executing `docker-compose`.

### **🔹 Development**
```bash
export ENVIRONMENT=dev
docker-compose up --build
```

### **🔹 QA**
```bash
export ENVIRONMENT=qa
docker-compose up --build -d
```

### **🔹 UAT**
```bash
export ENVIRONMENT=uat
docker-compose up --build -d
```

### **🔹 Production**
```bash
export ENVIRONMENT=prod
docker-compose up --build -d
```

---

## ✅ **Testing**
If the project includes tests, run them with:
```bash
pytest tests/ --disable-warnings --cov=app --cov-report=term-missing
```

To execute tests with **Docker**:

1️⃣ Accede al contenedor:
```bash
docker exec -it fastapi sh
```
2️⃣ Run the tests with pytest:
```bash
pytest tests/ --disable-warnings --cov=app --cov-report=term-missing
```
This will run the tests and display a coverage summary.

---

## 📜 **API Endpoints**
Once the service is running, check the interactive API documentation at:
```bash
📜 Swagger UI: http://localhost:8000/docs
```

```bash
📜 Redoc: http://localhost:8000/redoc
```

The API includes endpoints for:
- **Creating documents** in Elasticsearch
- **Searching documents**

---

## 🛠 **Tools & Technologies**
- 🐍 **Python 3.12**
- ⚡ **FastAPI**
- 🔍 **Elasticsearch**
- 🐳 **Docker & Docker Compose**
- 🏗 **Pydantic** for validations
- 🌿 **dotenv** for environment variable management

---

## 📌 **Contributing**
If you want to contribute to this project:
1. **Fork the repository**
2. **Create a branch (`feature/new-feature`)**
3. **Commit your changes (`git commit -m 'Add new feature'`)**
4. **Push to the branch (`git push origin feature/new-feature`)**
5. **Open a Pull Request** 🚀

---

## 🔗 **Author**
Developed by LA.

---

## 📜 **License**
This project is licensed under the MIT License. 📄