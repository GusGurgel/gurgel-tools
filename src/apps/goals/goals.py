from datetime import datetime, timezone
from typing import Annotated, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Field, Relationship, Session, SQLModel, select

from apps.engine import get_session  # As per your architectural pattern

SessionDep = Annotated[Session, Depends(get_session)]

# --- MOTIVATIONAL QUOTES (100 Quotes: Stoic & Biblical) ---
QUOTES = [
    "The impediment to action advances action. What stands in the way becomes the way. - Marcus Aurelius",
    "We suffer more often in imagination than in reality. - Seneca",
    "It's not what happens to you, but how you react to it that matters. - Epictetus",
    "I can do all things through Christ who strengthens me. - Philippians 4:13",
    "Waste no more time arguing what a good man should be. Be one. - Marcus Aurelius",
    "He who has a why to live for can bear almost any how. - Friedrich Nietzsche",
    "Commit your work to the Lord, and your plans will be established. - Proverbs 16:3",
    "No man is free who is not master of himself. - Epictetus",
    "Be strong and courageous. Do not be frightened, and do not be dismayed. - Joshua 1:9",
    "Luck is what happens when preparation meets opportunity. - Seneca",
    "The best revenge is to be unlike him who performed the injury. - Marcus Aurelius",
    "For God gave us a spirit not of fear but of power and love and self-control. - 2 Timothy 1:7",
    "First say to yourself what you would be; and then do what you have to do. - Epictetus",
    "As iron sharpens iron, so one person sharpens another. - Proverbs 27:17",
    "Let not your heart be troubled. - John 14:1",
    "Whatever can happen at any time can happen today. - Seneca",
    "You have power over your mind - not outside events. - Marcus Aurelius",
    "Trust in the Lord with all your heart, and do not lean on your own understanding. - Proverbs 3:5",
    "Man conquers the world by conquering himself. - Zeno of Citium",
    "A soft answer turns away wrath, but a harsh word stirs up anger. - Proverbs 15:1",
    "Difficulties strengthen the mind, as labor does the body. - Seneca",
    "Even if you walk through the valley of the shadow of death, fear no evil. - Psalm 23:4",
    "Wealth consists not in having great possessions, but in having few wants. - Epictetus",
    "Be completely humble and gentle; be patient, bearing with one another in love. - Ephesians 4:2",
    "The mind that is anxious about future events is miserable. - Seneca",
    "Let all that you do be done in love. - 1 Corinthians 16:14",
    "To be evenminded is the greatest virtue. - Heraclitus",
    "If any of you lacks wisdom, let him ask God. - James 1:5",
    "Ignorance is the cause of fear. - Seneca",
    "In all your ways acknowledge Him, and He will make straight your paths. - Proverbs 3:6",
    "Only time can heal what reason cannot. - Seneca",
    "The Lord is my light and my salvation; whom shall I fear? - Psalm 27:1",
    "How long are you going to wait before you demand the best for yourself? - Epictetus",
    "Take therefore no thought for the morrow. - Matthew 6:34",
    "He who fears death will never do anything worth of a man who is alive. - Seneca",
    "Walk by faith, not by sight. - 2 Corinthians 5:7",
    "If it is not right do not do it; if it is not true do not say it. - Marcus Aurelius",
    "The fear of the Lord is the beginning of knowledge. - Proverbs 1:7",
    "Sometimes even to live is an act of courage. - Seneca",
    "But the fruit of the Spirit is love, joy, peace, patience... - Galatians 5:22",
    "Don't explain your philosophy. Embody it. - Epictetus",
    "Come to me, all who labor and are heavy laden, and I will give you rest. - Matthew 11:28",
    "Dwell on the beauty of life. Watch the stars, and see yourself running with them. - Marcus Aurelius",
    "A joyful heart is good medicine, but a crushed spirit dries up the bones. - Proverbs 17:22",
    "It is quality rather than quantity that matters. - Seneca",
    "Seek first the kingdom of God and his righteousness. - Matthew 6:33",
    "Nothing, to my way of thinking, is a better proof of a well ordered mind than a man's ability to stop just where he is. - Seneca",
    "The Lord is my shepherd; I shall not want. - Psalm 23:1",
    "There is only one way to happiness and that is to cease worrying about things which are beyond the power or our will. - Epictetus",
    "And we know that for those who love God all things work together for good. - Romans 8:28",
    "Accept the things to which fate binds you, and love the people with whom fate brings you together. - Marcus Aurelius",
    "Be steadfast, immovable, always abounding in the work of the Lord. - 1 Corinthians 15:58",
    "To live a good life: We have the potential for it. If we can learn to be indifferent to what makes no difference. - Marcus Aurelius",
    "I have told you these things, so that in me you may have peace. - John 16:33",
    "No person has the power to have everything they want, but it is in their power not to want what they don't have. - Seneca",
    "Cast all your anxiety on him because he cares for you. - 1 Peter 5:7",
    "First learn the meaning of what you say, and then speak. - Epictetus",
    "For the wages of sin is death, but the free gift of God is eternal life. - Romans 6:23",
    "Very little is needed to make a happy life. - Marcus Aurelius",
    "For we are his workmanship, created in Christ Jesus for good works. - Ephesians 2:10",
    "Life is very short and anxious for those who forget the past, neglect the present, and fear the future. - Seneca",
    "My grace is sufficient for you, for my power is made perfect in weakness. - 2 Corinthians 12:9",
    "Any person capable of angering you becomes your master. - Epictetus",
    "And let us not grow weary of doing good. - Galatians 6:9",
    "The best answer to anger is silence. - Marcus Aurelius",
    "Draw near to God, and he will draw near to you. - James 4:8",
    "It is not the man who has too little, but the man who craves more, that is poor. - Seneca",
    "Be doers of the word, and not hearers only. - James 1:22",
    "Man is not worried by real problems so much as by his imagined anxieties about real problems. - Epictetus",
    "Whatever you do, work heartily, as for the Lord and not for men. - Colossians 3:23",
    "Our life is what our thoughts make it. - Marcus Aurelius",
    "Blessed are the peacemakers, for they shall be called sons of God. - Matthew 5:9",
    "True happiness is to enjoy the present, without anxious dependence upon the future. - Seneca",
    "For where your treasure is, there your heart will be also. - Matthew 6:21",
    "Circumstances don't make the man, they only reveal him to himself. - Epictetus",
    "Rejoice in hope, be patient in tribulation, be constant in prayer. - Romans 12:12",
    "When you arise in the morning think of what a privilege it is to be alive. - Marcus Aurelius",
    "Watch and pray that you may not enter into temptation. - Matthew 26:41",
    "While we are postponing, life speeds by. - Seneca",
    "We walk by faith, not by sight. - 2 Corinthians 5:7",
    "Know, first, who you are, and then adorn yourself accordingly. - Epictetus",
    "Above all else, guard your heart, for everything you do flows from it. - Proverbs 4:23",
    "Because a thing seems difficult for you, do not think it impossible. - Marcus Aurelius",
    "Set your minds on things that are above, not on things that are on earth. - Colossians 3:2",
    "Hang on to your youthful enthusiasms, you’ll be able to use them better when you’re older. - Seneca",
    "Be kind to one another, tenderhearted, forgiving one another. - Ephesians 4:32",
    "He who laughs at himself never runs out of things to laugh at. - Epictetus",
    "Therefore encourage one another and build one another up. - 1 Thessalonians 5:11",
    "Loss is nothing else but change, and change is Nature's delight. - Marcus Aurelius",
    "Whoever pursues righteousness and love finds life, prosperity and honor. - Proverbs 21:21",
    "Brave men rejoice in adversity, just as brave soldiers triumph in war. - Seneca",
    "Blessed is the man who remains steadfast under trial. - James 1:12",
    "Only the educated are free. - Epictetus",
    "For the Spirit God gave us does not make us timid, but gives us power. - 2 Timothy 1:7",
    "Conceal a flaw, and the world will imagine the worst. - Marcus Aurelius",
    "Let your light shine before others. - Matthew 5:16",
    "If you want to be loved, love. - Seneca",
    "A friend loves at all times, and a brother is born for a time of adversity. - Proverbs 17:17",
    "Make the best use of what is in your power, and take the rest as it happens. - Epictetus",
    "Whatever is true, whatever is honorable, whatever is just... think about these things. - Philippians 4:8",
]


# --- SQLMODELS ---
class Increment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    goal_id: int = Field(foreign_key="goal.id")
    value: int
    text: Optional[str] = None  # <--- NOVO CAMPO
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    goal: "Goal" = Relationship(back_populates="increments")


class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    target: int
    metric: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    increments: List[Increment] = Relationship(
        back_populates="goal", cascade_delete=True
    )


# --- PYDANTIC SCHEMAS ---
class GoalCreate(BaseModel):
    name: str
    target: int
    metric: str


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target: Optional[int] = None


class IncrementCreate(BaseModel):
    value: int
    text: Optional[str] = None  # <--- NOVO CAMPO
    image_url: Optional[str] = None


class IncrementUpdate(BaseModel):
    value: Optional[int] = None
    text: Optional[str] = None  # <--- NOVO CAMPO
    image_url: Optional[str] = None


class IncrementRead(BaseModel):
    id: int
    goal_id: int
    value: int
    text: Optional[str] = None  # <--- NOVO CAMPO
    image_url: Optional[str] = None
    created_at: datetime


class GoalRead(BaseModel):
    id: int
    name: str
    target: int
    metric: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    increments: List[IncrementRead] = []


def goals(app: FastAPI):

    @app.get("/api/goals/quote")
    def get_daily_quote():
        """Returns 1 of 100 quotes deterministically based on the day of the year."""
        day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
        quote_index = day_of_year % 100
        return {"quote": QUOTES[quote_index]}

    @app.get("/api/goals", response_model=List[GoalRead])
    def get_goals(session: SessionDep):
        """Fetches all goals. Sorted by the created_at of their latest increment DESC. Goals with no increments go to the bottom."""
        statement = select(Goal)
        db_goals = session.exec(statement).all()

        def get_sort_key(g: Goal):
            if not g.increments:
                # Retorna uma data muito antiga sem timezone (tz-naive)
                return datetime.min

            # Pega o created_at do incremento mais recente
            latest = max(inc.created_at for inc in g.increments)
            # Remove qualquer informação de timezone para garantir que o Python
            # não levante a exceção ao comparar com o datetime.min
            return latest.replace(tzinfo=None)

        sorted_goals = sorted(db_goals, key=get_sort_key, reverse=True)
        return sorted_goals

    @app.post("/api/goals", response_model=GoalRead)
    def create_goal(goal_in: GoalCreate, session: SessionDep):
        db_goal = Goal(**goal_in.dict())
        session.add(db_goal)
        session.commit()
        session.refresh(db_goal)
        return db_goal

    @app.put("/api/goals/{goal_id}", response_model=GoalRead)
    def update_goal(goal_id: int, goal_in: GoalUpdate, session: SessionDep):
        db_goal = session.get(Goal, goal_id)
        if not db_goal:
            raise HTTPException(status_code=404, detail="Goal not found")

        update_data = goal_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_goal, key, value)

        db_goal.updated_at = datetime.now(timezone.utc)
        session.add(db_goal)
        session.commit()
        session.refresh(db_goal)
        return db_goal

    @app.delete("/api/goals/{goal_id}")
    def delete_goal(goal_id: int, session: SessionDep):
        db_goal = session.get(Goal, goal_id)
        if not db_goal:
            raise HTTPException(status_code=404, detail="Goal not found")

        session.delete(db_goal)
        session.commit()
        return {"ok": True}

    @app.post("/api/goals/{goal_id}/complete", response_model=GoalRead)
    def complete_goal(goal_id: int, session: SessionDep):
        db_goal = session.get(Goal, goal_id)
        if not db_goal:
            raise HTTPException(status_code=404, detail="Goal not found")

        current_sum = sum(inc.value for inc in db_goal.increments)
        if current_sum < db_goal.target:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot complete. Progress ({current_sum}) is less than target ({db_goal.target}).",
            )

        db_goal.completed_at = datetime.now(timezone.utc)
        db_goal.updated_at = datetime.now(timezone.utc)
        session.add(db_goal)
        session.commit()
        session.refresh(db_goal)
        return db_goal

    @app.post("/api/goals/{goal_id}/increments", response_model=IncrementRead)
    def create_increment(goal_id: int, inc_in: IncrementCreate, session: SessionDep):
        db_goal = session.get(Goal, goal_id)
        if not db_goal:
            raise HTTPException(status_code=404, detail="Goal not found")

        db_inc = Increment(goal_id=goal_id, **inc_in.dict())
        session.add(db_inc)

        # Update goal's updated_at
        db_goal.updated_at = datetime.now(timezone.utc)
        session.add(db_goal)

        session.commit()
        session.refresh(db_inc)
        return db_inc

    @app.put("/api/increments/{inc_id}", response_model=IncrementRead)
    def update_increment(inc_id: int, inc_in: IncrementUpdate, session: SessionDep):
        db_inc = session.get(Increment, inc_id)
        if not db_inc:
            raise HTTPException(status_code=404, detail="Increment not found")

        update_data = inc_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_inc, key, value)

        session.add(db_inc)

        # Update parent goal's updated_at
        db_goal = session.get(Goal, db_inc.goal_id)
        if db_goal:
            db_goal.updated_at = datetime.now(timezone.utc)
            session.add(db_goal)

        session.commit()
        session.refresh(db_inc)
        return db_inc

    @app.delete("/api/increments/{inc_id}")
    def delete_increment(inc_id: int, session: SessionDep):
        db_inc = session.get(Increment, inc_id)
        if not db_inc:
            raise HTTPException(status_code=404, detail="Increment not found")

        goal_id = db_inc.goal_id
        session.delete(db_inc)

        db_goal = session.get(Goal, goal_id)
        if db_goal:
            db_goal.updated_at = datetime.now(timezone.utc)
            session.add(db_goal)

        session.commit()
        return {"ok": True}
