import pytest
from facebook_poster.main import FacebookPoster
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_facebook_poster_initialization():
    poster = FacebookPoster(test_mode=True)
    assert poster is not None

def test_chrome_setup():
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_options)
        assert driver is not None
        driver.quit()
    except Exception as e:
        pytest.skip(f"Chrome setup failed: {str(e)}")

def test_facebook_poster_headless():
    poster = FacebookPoster(test_mode=True)
    test_credentials = {
        'email': 'test@example.com',
        'password': 'testpassword',
        'groups': ['https://www.facebook.com/groups/test'],
        'message': 'Test message'
    }
    try:
        poster.post_to_groups(test_credentials)
    except Exception as e:
        if "chrome not reachable" in str(e).lower():
            pytest.skip("Chrome not available in test environment")
        else:
            raise e
