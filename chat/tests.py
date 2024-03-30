from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import ChatBot, Conversation, Message
from constants.header_constants import HEADER_USER_EMAIL


class GetMessageCountByBotTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "test@test.com"
        self.bot1 = ChatBot.objects.create(name='Bot 1', difficultyLevel=50)
        self.bot2 = ChatBot.objects.create(name='Bot 2', difficultyLevel=50)
        self.bot3 = ChatBot.objects.create(name='Bot 3', difficultyLevel=50)
        self.conversation1 = Conversation.objects.create(userEmail='user1@example.com', title='Conversation 1', bot=self.bot1)
        self.conversation2 = Conversation.objects.create(userEmail='user2@example.com', title='Conversation 2', bot=self.bot2)
        # Create messages for conversation 1
        Message.objects.create(senderEmail=self.email, senderType='user', messageText='Message 1', conversation=self.conversation1)
        Message.objects.create(senderEmail=self.email, senderType='bot', messageText='Message 2', conversation=self.conversation1)
        # Create messages for conversation 2
        Message.objects.create(senderEmail=self.email, senderType='user', messageText='Message 3', conversation=self.conversation2)
        Message.objects.create(senderEmail=self.email, senderType='bot', messageText='Message 4', conversation=self.conversation2)

    def test_get_message_count_by_bot(self):
        url = reverse('get_message_count_by_bot') + '?botId=' + str(self.bot1.id)
        headers = {HEADER_USER_EMAIL:self.email}
        response = self.client.get(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)  # Only one bot
        self.assertEqual(response.data["data"][0]['botId'], self.bot1.id)  # Bot 1's ID
        self.assertEqual(response.data["data"][0]['messageCount'], 2)  # Two messages in conversation 1

    def test_get_message_count_by_bot_invalid_bot_id(self):
        url = reverse('get_message_count_by_bot') + '?botId=invalid_bot_id'
        headers = {HEADER_USER_EMAIL:self.email}
        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_message_count_by_bot_no_authentication(self):
        url = reverse('get_message_count_by_bot') + '?botId=' + str(self.bot1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_message_count_by_bot_no_messages(self):
        url = reverse('get_message_count_by_bot') + '?botId=' + str(self.bot3.id)
        headers = {HEADER_USER_EMAIL:self.email}
        response = self.client.get(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 0)  # No bots, as there are no messages

class GetMessageCountAggregateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.email = "test@test.com"
        self.bot1 = ChatBot.objects.create(name='Bot 1', difficultyLevel=50)
        self.bot2 = ChatBot.objects.create(name='Bot 2', difficultyLevel=50)
        self.conversation1 = Conversation.objects.create(userEmail='user1@example.com', title='Conversation 1', bot=self.bot1)
        self.conversation2 = Conversation.objects.create(userEmail='user2@example.com', title='Conversation 2', bot=self.bot2)
        # Create messages for conversation 1
        Message.objects.create(senderEmail=self.email, senderType='user', messageText='Message 1', conversation=self.conversation1)
        Message.objects.create(senderEmail=self.email, senderType='user', messageText='Message 2', conversation=self.conversation1)
        # Create messages for conversation 2
        Message.objects.create(senderEmail=self.email, senderType='user', messageText='Message 3', conversation=self.conversation2)

    def test_get_message_count_aggregate(self):
        url = reverse('get_message_count_aggregate')
        headers = {HEADER_USER_EMAIL:self.email}
        response = self.client.get(url, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 2)  # Two bots
        # Go over the bot data
        for bot_data in response.data["data"]:
            if bot_data['botId'] == self.bot1.id:  # Check if bot 1's ID is found
                self.assertEqual(bot_data['messageCountByBot'], 2)  # Bot 1 has 2 messages
            elif bot_data['botId'] == self.bot2.id:  # Check if bot 2's ID is found
                self.assertEqual(bot_data['messageCountByBot'], 1)  # Bot 2 has 1 message
            else:
                # Unexpected bot ID encountered
                self.fail(f"Unexpected bot ID found in response data: {bot_data['botId']}")

    def test_get_message_count_aggregate_sort_asc(self):
        url = reverse('get_message_count_aggregate') + '?sort=asc'
        headers = {HEADER_USER_EMAIL:self.email}
        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"][0]['botId'], self.bot2.id)  # Bot 2's ID
        self.assertEqual(response.data["data"][1]['botId'], self.bot1.id)  # Bot 1's ID

    def test_get_message_count_aggregate_invalid_days_limit(self):
        url = reverse('get_message_count_aggregate') + '?daysLimit=invalid'
        headers = {HEADER_USER_EMAIL:self.email}
        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_message_count_aggregate_no_authentication(self):
        url = reverse('get_message_count_aggregate')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
