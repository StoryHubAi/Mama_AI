# 🚀 MAMA-AI Production Deployment Guide

## Pre-Deployment Checklist ✅

### 1. Environment Configuration
- [ ] Copy `.env.production` to `.env`
- [ ] Update Africa's Talking credentials (production keys)
- [ ] Set AI provider API key (OpenAI, Anthropic, or Google)
- [ ] Configure PostgreSQL database URL
- [ ] Generate secure SECRET_KEY (minimum 32 characters)
- [ ] Set FLASK_ENV=production

### 2. Database Setup
- [ ] Create PostgreSQL database
- [ ] Update DATABASE_URL in .env
- [ ] Test database connection locally

### 3. AI Model Integration
- [ ] Choose AI provider (OpenAI recommended)
- [ ] Add your API key to .env file
- [ ] Test AI responses with `/test-dashboard`
- [ ] Verify chat interface at `/chat-interface`

### 4. Africa's Talking Configuration
- [ ] Switch from sandbox to production environment
- [ ] Configure webhook URLs:
  - SMS: `https://your-app.herokuapp.com/sms`
  - USSD: `https://your-app.herokuapp.com/ussd`
  - Delivery Reports: `https://your-app.herokuapp.com/delivery-report`

## Heroku Deployment 🌐

### Step 1: Heroku Setup
```bash
# Install Heroku CLI if not already installed
# Create new Heroku app
heroku create mama-ai-health-assistant

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secure-secret-key
heroku config:set AFRICASTALKING_USERNAME=your-username
heroku config:set AFRICASTALKING_API_KEY=your-api-key
heroku config:set AFRICASTALKING_ENVIRONMENT=production
heroku config:set OPENAI_API_KEY=your-openai-key
```

### Step 2: Deploy
```bash
# Add files to git
git add .
git commit -m "Production-ready MAMA-AI deployment"

# Deploy to Heroku
git push heroku main

# Check logs
heroku logs --tail
```

### Step 3: Database Migration
```bash
# Run database migrations
heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Testing Production Deployment 🧪

### 1. Health Check
Visit: `https://your-app.herokuapp.com/health`
- Should show "healthy" status
- Database should be "connected"
- Africa's Talking should be "configured"

### 2. Test Dashboard
Visit: `https://your-app.herokuapp.com/test-dashboard`
- Test SMS responses
- Try quick test scenarios
- Check system status

### 3. Chat Interface
Visit: `https://your-app.herokuapp.com/chat-interface`
- Test AI conversations
- Verify multilingual support
- Check emergency detection

### 4. SMS Testing
Use Africa's Talking SMS simulator:
- Send test SMS to your shortcode
- Verify webhook responses
- Check delivery reports

## Production Monitoring 📊

### Health Endpoints
- `/health` - System health check
- `/stats` - Database statistics
- `/test-dashboard` - Interactive testing

### Logs
```bash
# View Heroku logs
heroku logs --tail

# Check specific components
heroku logs --grep="SMS"
heroku logs --grep="AI"
heroku logs --grep="ERROR"
```

## Security Considerations 🔒

1. **Environment Variables**
   - Never commit real API keys to git
   - Use strong SECRET_KEY
   - Rotate keys regularly

2. **Database Security**
   - Use PostgreSQL in production
   - Enable SSL connections
   - Regular backups

3. **API Rate Limiting**
   - Implement rate limiting for endpoints
   - Monitor usage patterns
   - Set appropriate timeouts

## Scaling Considerations 📈

### Performance Optimization
- Use Redis for caching
- Implement background tasks with Celery
- Monitor response times
- Scale workers as needed

### Database Optimization
- Add indexes for frequently queried fields
- Implement connection pooling
- Monitor query performance

## Troubleshooting 🔧

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check DATABASE_URL
   heroku config:get DATABASE_URL
   
   # Test connection
   heroku run python -c "from app import db; print(db.engine.url)"
   ```

2. **Africa's Talking Webhook Issues**
   - Verify webhook URLs in AT dashboard
   - Check endpoint accessibility
   - Review request logs

3. **AI Model Errors**
   - Verify API key is correct
   - Check rate limits
   - Monitor token usage

### Emergency Procedures
1. **Rollback Deployment**
   ```bash
   heroku rollback
   ```

2. **Database Recovery**
   ```bash
   heroku pg:backups:restore
   ```

3. **Scale Down**
   ```bash
   heroku ps:scale web=0
   ```

## Success Metrics 📊

Monitor these key metrics:
- Response time < 2 seconds
- 99.9% uptime
- SMS delivery rate > 95%
- User engagement metrics
- AI response accuracy

## Post-Deployment Tasks ✨

1. **User Training**
   - Create user guides
   - SMS command documentation
   - Emergency procedures

2. **Data Analytics**
   - Set up monitoring dashboards
   - Track user interactions
   - Monitor health advice patterns

3. **Continuous Improvement**
   - Collect user feedback
   - Improve AI prompts
   - Add new features based on usage

---

## Support & Maintenance 🛠️

### Regular Maintenance
- Weekly health checks
- Monthly dependency updates
- Quarterly security reviews
- AI model performance evaluation

### Documentation Updates
- Keep webhook URLs current
- Update API documentation
- Maintain deployment procedures

**Your MAMA-AI system is now production-ready! 🎉**

For issues or questions, check the logs and monitoring endpoints first.
