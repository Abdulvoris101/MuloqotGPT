from datetime import datetimefrom typing import Anyfrom pydantic import BaseModelfrom apps.core.models import Chatclass StatisticsReadScheme(BaseModel):    usersCount: int    activeUsers: int    activeUsersOfDay: int    usersUsedOneDay: int    usersUsedOneWeek: int    usersUsedOneMonth: int    premiumUsers: int    allMessages: int    avgUsersMessagesCount: Any    todayMessages: int    lastUpdate: datetime    latestUserId: int