from flask import Flask, redirect, url_for,render_template, session, request
import requests

app = Flask(__name__)
app.secret_key = 'your_flask_secret_key_here'  # Replace with your Flask app's secret key

# Directly setting Facebook App credentials
FB_APP_ID = '1413214649339539'
FB_APP_SECRET = 'b803cf8064d333684504f6887588058a'
FB_REDIRECT_URI = 'http://localhost:5000/login/callback'

@app.route('/')
def home():
    print(FB_APP_ID,FB_APP_SECRET)
    return render_template('index.html')

@app.route('/login')
def login():
    fb_login_url = f'https://www.facebook.com/v14.0/dialog/oauth?client_id={FB_APP_ID}&redirect_uri={FB_REDIRECT_URI}&scope=pages_show_list,pages_manage_posts,pages_read_engagement'
    return redirect(fb_login_url)


@app.route('/login/callback')
def login_callback():
    code = request.args.get('code')
    token_url = f'https://graph.facebook.com/v14.0/oauth/access_token?client_id={FB_APP_ID}&redirect_uri={FB_REDIRECT_URI}&client_secret={FB_APP_SECRET}&code={code}'
    token_response = requests.get(token_url).json()
    
    if 'error' in token_response:
        error_message = token_response['error'].get('message', 'An error occurred')
        return f'Error: {error_message}'
    
    access_token = token_response['access_token']
    session['access_token'] = access_token

    # Fetch user information
    user_info_url = f'https://graph.facebook.com/me?fields=id,name,picture&access_token={access_token}'
    user_info_response = requests.get(user_info_url).json()

    if 'error' in user_info_response:
        error_message = user_info_response['error'].get('message', 'An error occurred fetching user info')
        return f'Error: {error_message}'

    # Fetch pages information
    pages_info_url = f'https://graph.facebook.com/me/accounts?access_token={access_token}'
    pages_info_response = requests.get(pages_info_url).json()

    # Store each Page and its access token in the session
    if 'data' in pages_info_response:
        session['pages'] = [{'id': page['id'], 'access_token': page['access_token']} for page in pages_info_response['data']]
    else:
        return 'Failed to fetch Pages', 400

    pages = pages_info_response.get('data', [])

    return render_template('profile.html', name=user_info_response['name'], picture=user_info_response['picture']['data']['url'], pages=pages)


@app.route('/extend-token')
def extend_token():
    short_lived_token = session.get('access_token')
    if not short_lived_token:
        return redirect(url_for('login'))

    url = "https://graph.facebook.com/v14.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": FB_APP_ID,
        "client_secret": FB_APP_SECRET,
        "fb_exchange_token": short_lived_token
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'access_token' in data:
        long_lived_token = data['access_token']
        session['access_token'] = long_lived_token  # Update the session with the long-lived token
        print("Long-lived Token: ",long_lived_token)
        return f"Long-lived Token: {long_lived_token}"

    else:
        error_message = data.get('error', {}).get('message', 'Failed to extend token')
        return f"Error: {error_message}"


@app.route('/post-to-page', methods=['POST'])
def post_to_page():
    page_id = request.form['page_id']
    content = request.form['content']
    
    # Debug: Print or inspect the session data and form data
    print("Session 'pages':", session.get('pages'))
    print("Form submission - Page ID:", page_id)
    
    # Find the selected page's access token from session or database
    # Here, we're assuming you have stored the pages in the session like so:
    # session['pages'] = [{'id': page['id'], 'access_token': page['access_token']} for page in pages]
    pages = session.get('pages', [])
    page_access_token = next((page['access_token'] for page in pages if page['id'] == page_id), None)
    
    if not page_access_token:
        return 'Page access token not found', 400

    post_url = f'https://graph.facebook.com/{page_id}/feed'
    payload = {
        'message': content,
        'access_token': page_access_token
    }
    response = requests.post(post_url, data=payload).json()

    if 'error' in response:
        return f"Error posting to Page: {response['error'].get('message')}", 400

    return redirect(url_for('login_callback'))


if __name__ == '__main__':
    app.run(debug=True)
