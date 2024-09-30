import pytest

from app import schemas, models


@pytest.fixture
def test_vote(test_posts, session, test_user):
    new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user["id"])
    session.add(new_vote)
    session.commit()


def test_vote_post(authorized_client, test_posts):
    response = authorized_client.post("/vote/",
                                      json=schemas.Vote(post_id=test_posts[3].id, dir=schemas.VoteDir.up).model_dump())

    assert response.status_code == 201


def test_vote_twice_post(authorized_client, test_posts, test_vote):
    response = authorized_client.post("/vote/",
                                      json=schemas.Vote(post_id=test_posts[3].id, dir=schemas.VoteDir.up).model_dump())
    assert response.status_code == 409


def test_delete_vote(authorized_client, test_posts, test_vote):
    response = authorized_client.post("/vote/",
                                      json=schemas.Vote(post_id=test_posts[3].id,
                                                        dir=schemas.VoteDir.down).model_dump())
    assert response.status_code == 201


def test_delete_vote_not_voted_before(authorized_client, test_posts):
    response = authorized_client.post("/vote/",
                                      json=schemas.Vote(post_id=test_posts[3].id,
                                                        dir=schemas.VoteDir.down).model_dump())
    assert response.status_code == 404


def test_vote_post_not_exist(authorized_client, test_posts):
    response = authorized_client.post("/vote/",
                                      json=schemas.Vote(post_id=999999, dir=schemas.VoteDir.up).model_dump())
    assert response.status_code == 404


def test_unauthorized_user_vote_post(client, test_posts):
    response = client.post("/vote/",
                           json=schemas.Vote(post_id=test_posts[3].id,
                                             dir=schemas.VoteDir.down).model_dump())
    assert response.status_code == 401
