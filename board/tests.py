from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category

# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_kim = User.objects.create_user(username='kim', password='kimdjango')
        self.user_park = User.objects.create_user(username='park', password='parkdjango')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the world',
            category=self.category_programming,
            author=self.user_kim,
        )

        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부는 아니잖아요?',
            category=self.category_music,
            author=self.user_park,
        )
        self.post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='No category post',
            author=self.user_park,
        )

    def navbar_test(self, soup):
        # navbar 확인
        navbar = soup.nav
        # navbar 문구 확인
        self.assertIn('Board', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Community')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        board_btn = navbar.find('a', text='Board')
        self.assertEqual(board_btn.attrs['href'], '/board/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)


    def test_post_list(self):
        # 포스트가 존재함.
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/board/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('게시물이 존재하지 않습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)

        self.assertIn(self.user_kim.username.upper(), main_area.text)
        self.assertIn(self.user_park.username.upper(), main_area.text)

        #포스트가 미존재함.
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/board/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('게시물이 존재하지 않습니다', main_area.text)


    def test_post_detail(self):
        # 포스트가 존재함.

        # 포스트의 url = '/board/1/'
        self.assertEqual(self.post_001.get_absolute_url(), '/board/1/')

        # 상세페이지 테스트(첫번째 페이지)
        # url로 접근하면 정상적으로 작동함을 확인할 수 있음.(status code: 200)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # post_list페이지와 같은 navbar가 존재함.
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 포스트 제목을 웹 브라우저 탭의 title에서 확인가능
        self.assertIn(self.post_001.title, soup.title.text)

        # 포스트 제목이 포스트 영역에 존재
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)

        # 포스트 영역에 author 확인가능(구현)
        self.assertIn(self.user_kim.username.upper(), post_area.text)

        # 포스트 영역에 content-내용을 확인가능
        self.assertIn(self.post_001.content, post_area.text)