#include <time.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>

#define ALARM_FILE "alarm_time.txt"

time_t get_current_time(void)
{
	time_t current_time;
	time_t rawtime;
	struct tm * timeinfo;

	time (&rawtime);
	timeinfo = localtime ( &rawtime );
	printf ( "Current local time and date: %s", asctime (timeinfo) );
	current_time = mktime(timeinfo) - timezone;
	return current_time;
}

time_t parser_offset_time(char *time_str)
{
	time_t current_time;
	time_t rawtime;
	struct tm * timeinfo;
	int hour=0, min=0, sec=0;
	char *pch;
	int count=0;
	int number;
	
	pch = time_str;
	count += 2; // skip "0+"
	while(count < (strlen(time_str)-1))
	{
		number = atoi(pch+count);
		printf("number = %d,count =%d,time_str len=%d\n",number,count,strlen(time_str));
		while(1)
		{
			if(pch[count] =='h')
			{
				hour = number;
				printf("hour = %d\n",hour);
				count++;
				break;
			}
			else if (pch[count] == 'm')
			{
				min = number;
				printf("min = %d\n",min);
				count++;
				break;
			}
			else if (pch[count] == 's')
			{
				sec = number;
				printf("sec = %d\n",sec);
				count++;
				break;
			}
			count++;
		}
	}
	
	if(hour == 0 && min== 0 && sec == 0)
	{
		return (time_t)-1;
	}
	
	
	time (&rawtime);
	timeinfo = localtime ( &rawtime );
	printf ( "Current local time and date: %s", asctime (timeinfo) );
	timeinfo->tm_hour += hour;
	timeinfo->tm_min += min;
	timeinfo->tm_sec += sec;
	printf ( "Offset local time and date: %s", asctime (timeinfo) );
	current_time = mktime(timeinfo) - timezone;

	
	return current_time;
}

time_t get_alarm_time(char *time_str)
{
	
    struct tm tm = { 0 };

    if (strptime(time_str, "%Y-%m-%dT%H:%M:%S", &tm))
	{
		//Parse "2018-05-15T15:30:29"
		return mktime(&tm) - timezone;
	}
	else
	{
		//Parse "0+XXhXXmXXs"
		return parser_offset_time(time_str);
	}
	return (time_t)-1;
}

void get_alarm_time_from_file(char * filename, char * time)
{
	FILE * pFile;
	if(access(filename, F_OK)==0)
	{
		pFile = fopen (filename , "r");
		fgets(time , 32 , pFile);
		fclose(pFile);
		printf("File exist\n");
		//unlink(filename);
	}
	else
	{
		printf("File not exist\n");
	}
}

int main(int argc, char* argv[])
{
	char alarm_time_str[32]={0};
	
	time_t current_time;
	time_t alarm_time;
	int start_alarm;

	while(1)
	{
		memset(alarm_time_str, 0, sizeof(alarm_time_str));
		get_alarm_time_from_file(ALARM_FILE, alarm_time_str);
		if(strlen(alarm_time_str) != 0)
		{
			alarm_time = get_alarm_time(alarm_time_str);
			printf("alarm time   = %d\n", (int)alarm_time);
			if(alarm_time > 0)
			{
				start_alarm = 1;
			}
		}
		else
		{
			alarm_time = 0;
			printf("alarm time   = %d\n", (int)alarm_time);
		}		
		
		while(start_alarm)
		{
			current_time = get_current_time();
			printf("currnet time = %d\n", (int)current_time);
			
			if(access(ALARM_FILE, F_OK) !=0 )
			{
				printf("Alarm Cancel\n");
				start_alarm = 0;
			}
			
			if(current_time >=  alarm_time)
			{
				int alarm_count=0;
				printf("Wakeup!!\n");
				system ("aplay ring.wav");
				start_alarm = 0;
				unlink(ALARM_FILE);
			}
			sleep(1);
		}
		printf("Sleep\n");
		sleep(1);
	}
	
	return 0;
}