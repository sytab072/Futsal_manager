from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_list(self):
        #Postlist 로드
        response = self.client.get('/board/')
        #Page 로드
        self.assertEqual(response.status_code, 200)
        #페이지 이름은 'Board'
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Board')
        #navbar 확인
        navbar = soup.nav
        #navbar 문구 확인
        self.assertIn('Board', navbar.text)
        self.assertIn('About Me', navbar.text)

        #게시물 미존재시
        self.assertEqual(Post.objects.count(), 0)
        #게시물 없음 문구 확인
        main_area = soup.find('div', id='main-area')
        self.assertIn('게시물이 존재하지 않습니다', main_area.text)
        #게시물 두개 존재시
        post_001 = Post.objects.create(
            title='첫 번째 포스트입니다.',
            content='Hello World. We are the world',
        )
        post_002 = Post.objects.create(
            title='두 번째 포스트입니다.',
            content='1등이 전부는 아니잖아요?',
        )
        self.assertEqual(Post.objects.count(), 2)

        # post_list를 새로고침할시
        response = self.client.get('/board/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        # 타이틀 두개 존재(single_pages에)
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        # 이제 더 이상 게시물이 존재하지않는다는 문구는 보이지 않음.
        self.assertNotIn('이제 더 이상 게시물이 존재하지 않습니다', main_area.text)