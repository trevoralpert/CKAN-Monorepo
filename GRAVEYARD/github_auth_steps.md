# GitHub CLI Authentication Step-by-Step

## Method 1: Interactive Browser Authentication (Recommended)

### Step 1: Start the authentication
```bash
gh auth login
```

### Step 2: Answer the prompts exactly like this:

1. **"What account do you want to log into?"**
   - Select: `GitHub.com` (use arrow keys and press Enter)

2. **"What is your preferred protocol for Git operations?"**
   - Select: `HTTPS` (recommended for simplicity)

3. **"Authenticate Git with your GitHub credentials?"**
   - Select: `Yes`

4. **"How would you like to authenticate GitHub CLI?"**
   - Select: `Login with a web browser`

5. **You'll see a one-time code like: `XXXX-XXXX`**
   - Copy this code (you'll need it in the browser)
   - Press Enter to open the browser

6. **In your browser:**
   - Paste the one-time code
   - Click "Continue"
   - Click "Authorize github"
   - You should see "Congratulations, you're all set!"

7. **Back in terminal:**
   - You should see: "✓ Logged in as [your-username]"

## Method 2: Personal Access Token (If browser method fails)

### Step 1: Create a token on GitHub
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name like "GitHub CLI"
4. Select these scopes:
   - ✓ repo (all)
   - ✓ workflow
   - ✓ admin:public_key
5. Click "Generate token"
6. COPY THE TOKEN NOW (you won't see it again!)

### Step 2: Use the token
```bash
gh auth login
```

1. Select: `GitHub.com`
2. Select: `HTTPS`
3. Select: `Yes` (authenticate Git)
4. Select: `Paste an authentication token`
5. Paste your token and press Enter

## Verify It Worked

```bash
gh auth status
```

Should show:
```
✓ Logged in to github.com as [your-username]
✓ Git operations for github.com configured to use https protocol.
✓ Token: gho_************************************
```

## Common Issues

### "Connection refused" or browser doesn't open
- Copy the URL it shows and manually open it in your browser
- Or use Method 2 (token approach)

### "Bad credentials" error
- Make sure you copied the code correctly
- Try again with a fresh `gh auth login`

### Browser says "Device not found"
- You took too long - codes expire quickly
- Run `gh auth login` again for a fresh code

## Test Your Authentication
```bash
# This should list your repos
gh repo list --limit 5
```

If you see your repositories, you're all set! 