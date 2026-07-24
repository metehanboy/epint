#!/bin/bash
# Otomatik pull script - GitHub'dan güncellemeleri çeker
# Kullanım: ./auto-pull.sh veya cron job olarak çalıştırılabilir

REPO_DIR="/home/metehan/projects/portfolio_management/pip_packages/epint"
cd "$REPO_DIR" || exit 1

# SSH agent'ı başlat (eğer çalışmıyorsa)
if [ -z "$SSH_AUTH_SOCK" ]; then
    eval "$(ssh-agent -s)" > /dev/null 2>&1
    ssh-add ~/.ssh/id_rsa > /dev/null 2>&1
fi

# Mevcut branch'i al
current_branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')

echo "🔄 [$current_branch] Remote'tan güncellemeler kontrol ediliyor..."

# Remote'tan fetch yap
git fetch origin 2>&1 | grep -v "^$"

# Eğer local branch remote'tan gerideyse, pull yap
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u} 2>/dev/null)
BASE=$(git merge-base @ @{u} 2>/dev/null)

if [ "$REMOTE" != "" ] && [ "$LOCAL" != "$REMOTE" ] && [ "$LOCAL" = "$BASE" ]; then
    echo "📥 Yeni güncellemeler bulundu, pull yapılıyor..."
    git pull origin "$current_branch" 2>&1 | grep -v "^$"
    echo "✅ Güncellemeler tamamlandı!"
    exit 0
elif [ "$REMOTE" != "" ] && [ "$LOCAL" != "$REMOTE" ]; then
    echo "⚠️  Local branch remote'tan farklı, merge gerekebilir"
    exit 1
else
    echo "✅ Zaten güncel!"
    exit 0
fi

