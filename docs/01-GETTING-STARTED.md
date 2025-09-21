# Getting Started with Jetson AI System

## 🚀 Quick Start

The fastest way to get started with the complete Jetson AI system:

```bash
# Clone the repository
git clone https://github.com/DunaSpice/jetson-ai-system.git
cd jetson-ai-system

# Quick setup for Phase 3 (Production System)
cd phase3
./setup.sh

# Test the system
q chat "use get_status tool"
q chat "use generate tool with prompt 'Hello AI'"
```

## 📋 Prerequisites

### System Requirements
- **Hardware**: NVIDIA Jetson Orin Nano (or compatible)
- **OS**: Ubuntu 20.04+ (ARM64)
- **Memory**: 8GB+ RAM recommended
- **Storage**: 32GB+ available space
- **Python**: 3.10+

### Software Dependencies
- **Amazon Q CLI**: For MCP integration
- **Docker**: For containerized deployment
- **Git**: For version control
- **CUDA**: For GPU acceleration

## 🔧 Installation Options

### Option 1: Complete System Setup (Recommended)
```bash
# Full system with all phases
./setup_complete.sh
```

### Option 2: Phase-by-Phase Setup
```bash
# Phase 1: Basic web system
cd from_jetson_web/phase1
./setup_enhanced_system.sh

# Phase 3: MCP integration
cd ../../phase3
./setup.sh
```

### Option 3: Container-based Setup
```bash
# Using Jetson containers
cd jetson-containers
./install.sh
```

## 🎯 System Components

### Phase 1: Web-based Inference System
- **FastAPI server** with REST endpoints
- **Docker containerization** for easy deployment
- **Comprehensive testing suite** with stress tests
- **Performance monitoring** and optimization

### Phase 3: MCP Integration (Production)
- **Amazon Q CLI integration** via MCP protocol
- **Intelligent inference engine** with automatic model selection
- **Web frontend** with Next.js
- **C-based testing tools** for performance validation
- **Complete API documentation**

## 🧪 Verification

After installation, verify your system:

```bash
# Check Phase 3 MCP server
q chat "use get_status tool"

# Test text generation
q chat "use generate tool with prompt 'Test message'"

# Check system health
cd phase3
python3 test_comprehensive.py
```

## 📚 Next Steps

1. **Read the [Architecture Guide](./02-ARCHITECTURE.md)** to understand the system
2. **Explore [Phase 3 Documentation](./05-PHASE3.md)** for production features
3. **Review [API Reference](./09-API-REFERENCE.md)** for development
4. **Check [Testing Guide](./06-TESTING.md)** for validation procedures

## 🆘 Need Help?

- **Common Issues**: See [Troubleshooting Guide](./08-TROUBLESHOOTING.md)
- **Performance**: Check [Optimization Guide](./optimization/MEMORY.md)
- **Development**: Review [Development Notes](./10-DEVELOPMENT-NOTES.md)

---

*Complete setup typically takes 10-15 minutes on Jetson hardware.*
