from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status

from app.deps import CurrentUserDep, SessionDep
from app.models import Message, Post, Vote, VoteCreate

router = APIRouter(prefix="/votes", tags=["votes"])


# TODO: replace response_model with PostPublicWithVotes
@router.post("/", status_code=status.HTTP_200_OK, response_model=Message)
def add_or_remove_vote(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    vote: Annotated[VoteCreate, Body()],
) -> Message:
    post = session.get(Post, vote.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    db_vote = session.get(Vote, (current_user.id, vote.post_id))
    if vote.dir == 1:
        # If the vote direction is 1, we add (create) a vote
        if db_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Post has vote by current user",
            )
        new_vote = Vote(user_id=current_user.id, post_id=vote.post_id)
        session.add(new_vote)
        session.commit()
        return Message(message="successfully added vote")
    else:
        # If the vote direction is 0, we remove (delete) a vote
        if not db_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vote not found",
            )
        session.delete(db_vote)
        session.commit()
        return Message(message="successfully deleted vote")
