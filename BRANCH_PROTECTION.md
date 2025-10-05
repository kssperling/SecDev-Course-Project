# 🛡️ Branch Protection Rules

## Правила работы с main branch:

### 🚫 ЗАПРЕЩЕНО:
- Прямые пуши в main
- Мерж без ревью
- Мерж если не проходят тесты

### ✅ ОБЯЗАТЕЛЬНО:
1. Создавать feature branch:
   \`\`\`bash
   git checkout -b p02-feature-name
   \`\`\`

2. Создавать Pull Request:
   \`\`\`bash
   git push origin p02-feature-name
   # Затем создать PR на GitHub
   \`\`\`

3. Получить минимум 1 апрув

4. Убедиться что все тесты проходят

## Аварийные ситуации:
Для хотфиксов создавать \`hotfix/\` ветки и получать экстренное ревью.
