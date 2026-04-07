"""
Comprehensive test suite for the Mergington High School API
Tests all endpoints with success and error cases
"""
import pytest

class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client, reset_activities):
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client, reset_activities):
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_all_activities(self, client, reset_activities):
        response = client.get("/activities")
        activities_data = response.json()
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Soccer Club", "Art Club", "Drama Club", "Debate Club", "Science Club"
        ]
        for activity in expected_activities:
            assert activity in activities_data

    def test_get_activities_activity_has_required_fields(self, client, reset_activities):
        response = client.get("/activities")
        activities_data = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for activity_name, activity_data in activities_data.items():
            for field in required_fields:
                assert field in activity_data

    def test_get_activities_participants_is_list(self, client, reset_activities):
        response = client.get("/activities")
        activities_data = response.json()
        for activity_data in activities_data.values():
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_contains_existing_participants(self, client, reset_activities):
        response = client.get("/activities")
        activities_data = response.json()
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]
        assert "emma@mergington.edu" in activities_data["Programming Class"]["participants"]

class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success_returns_200(self, client, reset_activities, sample_email):
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200

    def test_signup_success_returns_correct_message(self, client, reset_activities, sample_email):
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert sample_email in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities, sample_email):
        response = client.post(
            "/activities/Soccer Club/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert sample_email in activities_data["Soccer Club"]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities, sample_email):
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_returns_400(self, client, reset_activities):
        email = "michael@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        response1 = client.post(
            "/activities/Art Club/signup",
            params={"email": email1}
        )
        response2 = client.post(
            "/activities/Art Club/signup",
            params={"email": email2}
        )
        assert response1.status_code == 200
        assert response2.status_code == 200
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email1 in activities_data["Art Club"]["participants"]
        assert email2 in activities_data["Art Club"]["participants"]

    def test_signup_same_student_different_activities(self, client, reset_activities, sample_email):
        response1 = client.post(
            "/activities/Debate Club/signup",
            params={"email": sample_email}
        )
        response2 = client.post(
            "/activities/Drama Club/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        assert response2.status_code == 200
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert sample_email in activities_data["Debate Club"]["participants"]
        assert sample_email in activities_data["Drama Club"]["participants"]

    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        special_email = "student+tag@mergington.edu"
        response = client.post(
            "/activities/Science Club/signup",
            params={"email": special_email}
        )
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert special_email in activities_data["Science Club"]["participants"]

class TestRemoveParticipant:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_remove_participant_success_returns_200(self, client, reset_activities):
        email = "michael@mergington.edu"
        response = client.delete(
            f"/activities/Chess Club/participants/{email}"
        )
        assert response.status_code == 200

    def test_remove_participant_success_returns_correct_message(self, client, reset_activities):
        email = "daniel@mergington.edu"
        response = client.delete(
            f"/activities/Chess Club/participants/{email}"
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email in response.json()["message"]

    def test_remove_participant_actually_removes(self, client, reset_activities):
        email = "emma@mergington.edu"
        response = client.delete(
            f"/activities/Programming Class/participants/{email}"
        )
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Programming Class"]["participants"]

    def test_remove_nonexistent_activity_returns_404(self, client, reset_activities):
        response = client.delete(
            "/activities/Nonexistent Club/participants/test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_nonexistent_participant_returns_404(self, client, reset_activities):
        response = client.delete(
            "/activities/Chess Club/participants/nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_participant_twice_returns_404(self, client, reset_activities):
        email = "john@mergington.edu"
        response1 = client.delete(
            f"/activities/Gym Class/participants/{email}"
        )
        assert response1.status_code == 200
        response2 = client.delete(
            f"/activities/Gym Class/participants/{email}"
        )
        assert response2.status_code == 404

    def test_remove_then_signup_same_participant(self, client, reset_activities, sample_email):
        response1 = client.post(
            "/activities/Drama Club/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        response2 = client.delete(
            f"/activities/Drama Club/participants/{sample_email}"
        )
        assert response2.status_code == 200
        response3 = client.post(
            "/activities/Drama Club/signup",
            params={"email": sample_email}
        )
        assert response3.status_code == 200
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert sample_email in activities_data["Drama Club"]["participants"]

    def test_remove_participant_with_special_characters_in_email(self, client, reset_activities):
        special_email = "student+test@mergington.edu"
        response1 = client.post(
            "/activities/Soccer Club/signup",
            params={"email": special_email}
        )
        assert response1.status_code == 200
        response2 = client.delete(
            f"/activities/Soccer Club/participants/{special_email}"
        )
        assert response2.status_code == 200

class TestIntegration:
    """Integration tests combining multiple endpoints"""

    def test_signup_and_verify_in_listing(self, client, reset_activities, sample_email):
        signup_response = client.post(
            "/activities/Art Club/signup",
            params={"email": sample_email}
        )
        assert signup_response.status_code == 200
        list_response = client.get("/activities")
        assert list_response.status_code == 200
        activities_data = list_response.json()
        assert sample_email in activities_data["Art Club"]["participants"]

    def test_full_lifecycle_signup_remove_signup(self, client, reset_activities, sample_email):
        activity = "Debate Club"
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        response2 = client.delete(
            f"/activities/{activity}/participants/{sample_email}"
        )
        assert response2.status_code == 200
        response3 = client.post(
            f"/activities/{activity}/signup",
            params={"email": sample_email}
        )
        assert response3.status_code == 200
        final_response = client.get("/activities")
        activities_data = final_response.json()
        assert sample_email in activities_data[activity]["participants"]

    def test_multiple_operations_maintain_state(self, client, reset_activities):
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        activity = "Science Club"
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email1}
        )
        assert response1.status_code == 200
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email2}
        )
        assert response2.status_code == 200
        response3 = client.delete(
            f"/activities/{activity}/participants/{email1}"
        )
        assert response3.status_code == 200
        final_response = client.get("/activities")
        activities_data = final_response.json()
        assert email1 not in activities_data[activity]["participants"]
        assert email2 in activities_data[activity]["participants"]
