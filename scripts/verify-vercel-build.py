#!/usr/bin/env python3
"""
Vercel部署验证脚本
验证构建配置和部署准备情况
"""

import os
import json
import subprocess
import sys
from pathlib import Path

class VercelBuildVerifier:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.frontend_dir = self.project_root / "frontend"
        self.errors = []
        self.warnings = []
        
    def log_error(self, message):
        self.errors.append(message)
        print(f"❌ {message}")
        
    def log_warning(self, message):
        self.warnings.append(message)
        print(f"⚠️ {message}")
        
    def log_success(self, message):
        print(f"✅ {message}")
        
    def check_vercel_config(self):
        """检查Vercel配置文件"""
        print("\n🔍 检查Vercel配置...")
        
        # 检查vercel.json
        vercel_config = self.project_root / "vercel.json"
        if not vercel_config.exists():
            self.log_error("vercel.json 文件不存在")
            return False
            
        try:
            with open(vercel_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 验证必要字段
            if "builds" not in config:
                self.log_error("vercel.json 缺少 builds 配置")
            else:
                self.log_success("vercel.json builds 配置正确")
                
            if "routes" not in config:
                self.log_error("vercel.json 缺少 routes 配置")
            else:
                self.log_success("vercel.json routes 配置正确")
                
        except json.JSONDecodeError:
            self.log_error("vercel.json 格式错误")
            return False
            
        # 检查.vercelignore
        vercelignore = self.project_root / ".vercelignore"
        if vercelignore.exists():
            self.log_success(".vercelignore 文件存在")
        else:
            self.log_warning(".vercelignore 文件不存在")
            
        return True
    
    def check_frontend_config(self):
        """检查前端配置"""
        print("\n🎨 检查前端配置...")
        
        # 检查package.json
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            self.log_error("frontend/package.json 不存在")
            return False
            
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                package = json.load(f)
                
            # 检查构建脚本
            scripts = package.get("scripts", {})
            if "build" not in scripts:
                self.log_error("package.json 缺少 build 脚本")
            else:
                self.log_success("package.json build 脚本存在")
                
            if "vercel-build" not in scripts:
                self.log_warning("package.json 缺少 vercel-build 脚本")
            else:
                self.log_success("package.json vercel-build 脚本存在")
                
            # 检查依赖
            dependencies = package.get("dependencies", {})
            dev_dependencies = package.get("devDependencies", {})
            
            required_deps = ["vue", "vue-router", "pinia"]
            for dep in required_deps:
                if dep in dependencies:
                    self.log_success(f"依赖 {dep} 存在")
                else:
                    self.log_error(f"缺少依赖 {dep}")
                    
            if "vite" in dev_dependencies:
                self.log_success("构建工具 vite 存在")
            else:
                self.log_error("缺少构建工具 vite")
                
        except json.JSONDecodeError:
            self.log_error("package.json 格式错误")
            return False
            
        return True
    
    def check_vite_config(self):
        """检查Vite配置"""
        print("\n⚡ 检查Vite配置...")
        
        vite_config = self.frontend_dir / "vite.config.js"
        if not vite_config.exists():
            self.log_error("vite.config.js 不存在")
            return False
            
        try:
            with open(vite_config, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查关键配置
            if "outDir: 'dist'" in content:
                self.log_success("输出目录配置正确")
            else:
                self.log_warning("输出目录配置可能有问题")
                
            if "VitePWA" in content:
                self.log_success("PWA插件配置存在")
            else:
                self.log_warning("PWA插件配置缺失")
                
            if "base: '/'" in content:
                self.log_success("基础路径配置正确")
            else:
                self.log_warning("基础路径配置可能有问题")
                
        except Exception as e:
            self.log_error(f"读取vite.config.js失败: {str(e)}")
            return False
            
        return True
    
    def check_env_files(self):
        """检查环境变量文件"""
        print("\n🌍 检查环境变量配置...")
        
        env_files = [
            (".env.production", "生产环境配置"),
            (".env.development", "开发环境配置")
        ]
        
        for filename, description in env_files:
            env_file = self.frontend_dir / filename
            if env_file.exists():
                self.log_success(f"{description} 文件存在")
                
                # 检查关键变量
                try:
                    with open(env_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    if "VITE_API_BASE_URL" in content:
                        self.log_success(f"{description} 包含API配置")
                    else:
                        self.log_warning(f"{description} 缺少API配置")
                        
                except Exception as e:
                    self.log_error(f"读取 {filename} 失败: {str(e)}")
            else:
                self.log_warning(f"{description} 文件不存在")
    
    def test_build(self):
        """测试构建过程"""
        print("\n🏗️ 测试构建过程...")
        
        try:
            # 切换到前端目录
            os.chdir(self.frontend_dir)
            
            # 检查node_modules
            if not (self.frontend_dir / "node_modules").exists():
                print("📦 安装依赖...")
                result = subprocess.run(["npm", "install"], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_error(f"依赖安装失败: {result.stderr}")
                    return False
                else:
                    self.log_success("依赖安装成功")
            
            # 执行构建
            print("🔨 执行构建...")
            result = subprocess.run(["npm", "run", "build"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_success("构建成功")
                
                # 检查构建产物
                dist_dir = self.frontend_dir / "dist"
                if dist_dir.exists():
                    self.log_success("dist 目录存在")
                    
                    # 检查关键文件
                    key_files = ["index.html", "manifest.json"]
                    for file in key_files:
                        if (dist_dir / file).exists():
                            self.log_success(f"{file} 存在")
                        else:
                            self.log_warning(f"{file} 不存在")
                            
                    # 检查assets目录
                    assets_dir = dist_dir / "assets"
                    if assets_dir.exists():
                        asset_files = list(assets_dir.glob("*"))
                        self.log_success(f"assets 目录包含 {len(asset_files)} 个文件")
                    else:
                        self.log_warning("assets 目录不存在")
                        
                else:
                    self.log_error("构建产物 dist 目录不存在")
                    return False
                    
            else:
                self.log_error(f"构建失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_error(f"构建测试失败: {str(e)}")
            return False
        finally:
            # 切换回项目根目录
            os.chdir(self.project_root)
            
        return True
    
    def generate_report(self):
        """生成验证报告"""
        print("\n" + "="*50)
        print("📊 Vercel部署验证报告")
        print("="*50)
        
        if not self.errors:
            print("🎉 所有检查通过！项目已准备好部署到Vercel")
            print("\n📋 下一步操作:")
            print("1. 访问 https://vercel.com/dashboard")
            print("2. 点击 'New Project'")
            print("3. 选择 GitHub 仓库: wangpeng1017/SOUND")
            print("4. 配置项目设置:")
            print("   - Framework: Vue.js")
            print("   - Root Directory: frontend")
            print("   - Build Command: npm run build")
            print("   - Output Directory: dist")
            print("5. 设置环境变量:")
            print("   - VITE_API_BASE_URL=https://your-backend-api.herokuapp.com")
            print("6. 点击 'Deploy'")
        else:
            print(f"❌ 发现 {len(self.errors)} 个错误需要修复:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
                
        if self.warnings:
            print(f"\n⚠️ 发现 {len(self.warnings)} 个警告:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
                
        return len(self.errors) == 0
    
    def run_verification(self):
        """运行完整验证"""
        print("🚀 开始Vercel部署验证...")
        
        # 执行各项检查
        self.check_vercel_config()
        self.check_frontend_config()
        self.check_vite_config()
        self.check_env_files()
        self.test_build()
        
        # 生成报告
        success = self.generate_report()
        
        return success

def main():
    verifier = VercelBuildVerifier()
    success = verifier.run_verification()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
