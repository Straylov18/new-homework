import pytest
from httpx import AsyncClient


class TestUsers:

    @pytest.mark.parametrize(
        ("user_name", "user_email"),
        [
            ("Biba", "bib@mail.ru"),
            ("Bop", "bop@gmail.com"),
            ("Trumpgpt", "Trump@gpt.gov"),
            ("Фронтендер! Не", "коммить@node_modules.плз"),
            ("Alice Johnson", "alice.johnson@example.com"),
            ("Bob Smith", "bob.smith@example.com"),
            ("Carol Davis", "carol.davis@example.com"),
            ("David Lee", "david.lee@example.com"),
            ("Eva Martinez", "eva.martinez@example.com"),
            ("Ethan Reed", "ethan.reed@example.com"),
            ("Mia Thompson", "mia.thompson@example.com"),
            ("Liam Carter", "liam.carter@example.com"),
            ("Sophia Parker", "sophia.parker@example.com"),
            ("Noah Evans", "noah.evans@example.com"),
            ("Isabella Mitchell", "isabella.mitchell@example.com"),
            ("Oliver Ross", "oliver.ross@example.com"),
            ("Amelia Fisher", "amelia.fisher@example.com"),
            ("James Perry", "james.perry@example.com"),
            ("Harper Hughes", "harper.hughes@example.com"),
            ("William Gray", "william.gray@example.com"),
            ("Ava Bennett", "ava.bennett@example.com"),
            ("Benjamin Jenkins", "benjamin.jenkins@example.com"),
            ("Charlotte Powell", "charlotte.powell@example.com"),
            ("Lucas Hayes", "lucas.hayes@example.com"),
            ("Victoria Foster", "victoria.foster@example.com"),
            ("Henry Richardson", "henry.richardson@example.com"),
            ("Luna Collins", "luna.collins@example.com"),
            ("Alexander Stewart", "alexander.stewart@example.com"),
            ("Zoey Morris", "zoey.morris@example.com"),
        ]
    )
    @pytest.mark.asyncio
    async def test_user(self, async_client: AsyncClient, user_name: str, user_email: str):
        response_1 = await async_client.post('/api/v1/user/', json={'name': user_name, 'email': user_email})
        assert response_1.status_code == 200

        response_2 = await async_client.post('/api/v1/user/', json={'name': user_name, 'email': user_email})
        assert response_2.status_code == 200

        response_list = await async_client.get('/api/v1/user/list')
        assert len(response_list.json()) == 2
