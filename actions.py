from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import re

# Keep an in-memory task list
TASK_LOG = []


class ActionAddTask(Action):
    def name(self) -> Text:
        return "action_add_task"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # --- Improved extraction logic ---
        user_message = tracker.latest_message.get("text", "").lower()

        # Try regex to capture full task phrase
        match = re.search(r"(?:add (?:a )?task (?:to )?)(.*)", user_message)
        if match:
            task = match.group(1).strip()
        else:
            task = next(tracker.get_latest_entity_values("task"), None)

        deadline = next(tracker.get_latest_entity_values("deadline"), None)
        priority = next(tracker.get_latest_entity_values("priority"), None)

        if not task:
            dispatcher.utter_message("Please tell me the task you want to add.")
            return []

        entry = {
            "task": task,
            "deadline": deadline or "unspecified",
            "priority": priority or "medium"
        }
        TASK_LOG.append(entry)

        dispatcher.utter_message(
            f"✅ Task added: '{entry['task']}' with deadline '{entry['deadline']}' and priority '{entry['priority']}'."
        )
        return []


class ActionShowTasks(Action):
    def name(self) -> Text:
        return "action_show_tasks"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if not TASK_LOG:
            dispatcher.utter_message("Your task list is empty. Add something first!")
            return []

        message = "📝 Here are your current tasks:\n"
        for i, t in enumerate(TASK_LOG, 1):
            message += f"{i}. {t['task']} — Deadline: {t['deadline']}, Priority: {t['priority']}\n"

        dispatcher.utter_message(message)
        return []


class ActionStressResponse(Action):
    def name(self) -> Text:
        return "action_stress_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        level = next(tracker.get_latest_entity_values("stress_level"), None)

        try:
            level = int(level)
        except (TypeError, ValueError):
            dispatcher.utter_message("Please give a number between 1 and 10.")
            return []

        if 1 <= level <= 5:
            dispatcher.utter_message("💪 Stay strong! Remember: progress, not perfection. You’ve got this!")
        elif 6 <= level <= 8:
            dispatcher.utter_message("🧘 Try 5 minutes of deep breathing or meditation — it really helps.")
        elif 9 <= level <= 10:
            dispatcher.utter_message("❤️ That sounds tough. Please reach out for support:\n- https://findahelpline.com\n- https://mentalhealth.gov\nYou're not alone.")
        else:
            dispatcher.utter_message("Please rate stress between 1 and 10.")

        return []

class ActionMarkTaskDone(Action):
    def name(self) -> Text:
        return "action_mark_task_done"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        task_name = next(tracker.get_latest_entity_values("task"), None)
        if not task_name:
            dispatcher.utter_message("Please tell me which task you’ve completed.")
            return []

        global TASK_LOG
        for t in TASK_LOG:
            if task_name.lower() in t['task'].lower():
                TASK_LOG.remove(t)
                dispatcher.utter_message(f"✅ Marked '{task_name}' as completed and removed it from your list!")
                return []

        dispatcher.utter_message(f"❌ I couldn’t find '{task_name}' in your task list.")
        return []
