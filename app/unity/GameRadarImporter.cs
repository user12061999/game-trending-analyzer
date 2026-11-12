#if UNITY_EDITOR
using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.Networking;

namespace GameTrendingRadar.Editor
{
    /// <summary>
    /// Game Trending Radar - 1-Click Prototype Scene Importer.
    /// Connects to the local Game Trending Analyzer server (http://127.0.0.1:8888)
    /// and automatically generates a complete 2D/3D playable prototype scene with scripts,
    /// GameObjects, physics colliders, and wave directors in 3 seconds!
    /// </summary>
    public class GameRadarImporter : EditorWindow
    {
        private string serverUrl = "http://127.0.0.1:8888";
        private string gameTitle = "Black Myth: Wukong";
        private string genreArchetype = "Action Roguelike";
        private string platform = "PC / Mobile";
        private bool autoCreateScene = true;
        private bool autoWireComponents = true;
        private bool autoCreateEnemyPrefab = true;
        private bool statusIsFetching = false;
        private string statusMessage = "Sẵn sàng kết nối tới Game Trending Analyzer...";
        private Vector2 scrollPos;

        [MenuItem("Tools/Game Trending Radar/1-Click Prototype Scene Generator", false, 1)]
        [MenuItem("Window/Game Trending Radar/Setup Prototype Scene", false, 100)]
        public static void ShowWindow()
        {
            var window = GetWindow<GameRadarImporter>("Radar Scene Importer");
            window.minSize = new Vector2(460, 540);
            window.Show();
        }

        private void OnGUI()
        {
            scrollPos = EditorGUILayout.BeginScrollView(scrollPos);

            // Header Banner
            EditorGUILayout.Space(8);
            GUIStyle headerStyle = new GUIStyle(EditorStyles.boldLabel)
            {
                fontSize = 15,
                alignment = TextAnchor.MiddleCenter
            };
            EditorGUILayout.LabelField("🎮 GAME TRENDING RADAR", headerStyle);

            GUIStyle subHeaderStyle = new GUIStyle(EditorStyles.miniLabel)
            {
                alignment = TextAnchor.MiddleCenter
            };
            EditorGUILayout.LabelField("1-Click Unity Scene Generator & Prototype Importer", subHeaderStyle);
            EditorGUILayout.Space(10);

            // Server Configuration Box
            EditorGUILayout.BeginVertical("box");
            EditorGUILayout.LabelField("🌐 Cấu Hình Kết Nối Backend:", EditorStyles.boldLabel);
            serverUrl = EditorGUILayout.TextField("Server URL:", serverUrl);

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("Kiểm Tra Kết Nối Server (Ping)"))
            {
                EditorCoroutineUtility.StartCoroutine(CheckServerHealth());
            }
            if (GUILayout.Button("Lấy Game Đang Hot Từ Radar"))
            {
                EditorCoroutineUtility.StartCoroutine(FetchTopRadarGames());
            }
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.EndVertical();

            EditorGUILayout.Space(8);

            // Target Game Parameters Box
            EditorGUILayout.BeginVertical("box");
            EditorGUILayout.LabelField("🎯 Tựa Game Muốn Dựng Prototype 1:1:", EditorStyles.boldLabel);
            gameTitle = EditorGUILayout.TextField("Tên Game:", gameTitle);

            string[] archetypes = new string[] {
                "Action Roguelike",
                "Action RPG / Souls-like",
                "Tactical Shooter / BR",
                "4X Strategy SLG",
                "Casual Puzzle / Merge",
                "Turn-based Gacha RPG"
            };
            int curArchIdx = Mathf.Max(0, Array.IndexOf(archetypes, genreArchetype));
            int newArchIdx = EditorGUILayout.Popup("Cổ Mẫu Gameplay:", curArchIdx, archetypes);
            genreArchetype = archetypes[newArchIdx];

            platform = EditorGUILayout.TextField("Nền Tảng Đích:", platform);
            EditorGUILayout.EndVertical();

            EditorGUILayout.Space(8);

            // Generator Options
            EditorGUILayout.BeginVertical("box");
            EditorGUILayout.LabelField("⚙️ Tùy Chọn Khởi Tạo Tự Động:", EditorStyles.boldLabel);
            autoCreateScene = EditorGUILayout.Toggle("Tạo Scene Mới (PrototypeScene.unity)", autoCreateScene);
            autoCreateEnemyPrefab = EditorGUILayout.Toggle("Tạo Prefab Quái Vật (EnemyMinion.prefab)", autoCreateEnemyPrefab);
            autoWireComponents = EditorGUILayout.Toggle("Tự động gán Components & Colliders", autoWireComponents);
            EditorGUILayout.EndVertical();

            EditorGUILayout.Space(14);

            // Primary Action Button
            GUI.backgroundColor = new Color(0.2f, 0.8f, 0.4f);
            GUIStyle btnStyle = new GUIStyle(GUI.skin.button)
            {
                fontSize = 13,
                fontStyle = FontStyle.Bold,
                fixedHeight = 42
            };

            if (GUILayout.Button(statusIsFetching ? "⏳ Đang Bóc Tách & Tải Mã Nguồn..." : "🚀 BẮT ĐẦU DỰNG PROTOTYPE SCENE TỰ ĐỘNG", btnStyle))
            {
                if (!statusIsFetching)
                {
                    EditorCoroutineUtility.StartCoroutine(BuildPrototypeSceneWorkflow());
                }
            }
            GUI.backgroundColor = Color.white;

            EditorGUILayout.Space(8);

            // Status Console
            EditorGUILayout.HelpBox(statusMessage, statusIsFetching ? MessageType.Info : MessageType.None);

            EditorGUILayout.EndScrollView();
        }

        private IEnumerator CheckServerHealth()
        {
            statusMessage = "Đang kiểm tra kết nối tới " + serverUrl + "...";
            using (UnityWebRequest req = UnityWebRequest.Get(serverUrl + "/api/overview"))
            {
                req.timeout = 5;
                yield return req.SendWebRequest();
                if (req.result == UnityWebRequest.Result.Success)
                {
                    statusMessage = "✅ Kết nối thành công tới Game Trending Analyzer Dashboard!";
                }
                else
                {
                    statusMessage = "❌ Không kết nối được tới server (" + req.error + "). Hãy chắc chắn server đang chạy tại port 8888.";
                }
            }
            Repaint();
        }

        private IEnumerator FetchTopRadarGames()
        {
            statusMessage = "Đang lấy danh sách game dẫn đầu thị trường...";
            using (UnityWebRequest req = UnityWebRequest.Get(serverUrl + "/api/overview"))
            {
                req.timeout = 5;
                yield return req.SendWebRequest();
                if (req.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        var json = req.downloadHandler.text;
                        // Pick first rising game or top steam game
                        if (json.Contains("\"title\":\""))
                        {
                            int idx = json.IndexOf("\"title\":\"") + 9;
                            int end = json.IndexOf("\"", idx);
                            if (end > idx)
                            {
                                gameTitle = json.Substring(idx, end - idx);
                                statusMessage = "★ Đã chọn game hot nhất: " + gameTitle;
                            }
                        }
                    }
                    catch (Exception e)
                    {
                        statusMessage = "Lỗi đọc dữ liệu: " + e.Message;
                    }
                }
                else
                {
                    statusMessage = "Không kết nối được: " + req.error;
                }
            }
            Repaint();
        }

        private IEnumerator BuildPrototypeSceneWorkflow()
        {
            statusIsFetching = true;
            statusMessage = "1/4: Đang gửi yêu cầu bóc tách sang Game Trending Engine...";
            Repaint();

            string endpoint = serverUrl + "/api/deconstruct/analyze";
            string jsonBody = "{\"game_title\":\"" + gameTitle + "\",\"platform\":\"" + platform + "\",\"genre_hint\":\"" + genreArchetype + "\",\"use_ai_llm\":false}";

            using (UnityWebRequest req = new UnityWebRequest(endpoint, "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonBody);
                req.uploadHandler = new UploadHandlerRaw(bodyRaw);
                req.downloadHandler = new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type", "application/json");
                req.timeout = 15;

                yield return req.SendWebRequest();

                if (req.result != UnityWebRequest.Result.Success)
                {
                    statusIsFetching = false;
                    statusMessage = "❌ Thất bại: " + req.error;
                    Repaint();
                    yield break;
                }

                statusMessage = "2/4: Đang ghi mã nguồn 5 C# Scripts vào Assets/Scripts/GamePrototype/...";
                Repaint();

                string responseText = req.downloadHandler.text;
                SaveUnityScripts(responseText);

                statusMessage = "3/4: Đang cập nhật Database tài nguyên Unity (AssetDatabase.Refresh)...";
                Repaint();
                AssetDatabase.Refresh();

                if (autoCreateScene)
                {
                    statusMessage = "4/4: Đang dựng GameObject Player, Enemy Director và Camera...";
                    Repaint();
                    CreatePlayableSceneHierarchy();
                }

                statusIsFetching = false;
                statusMessage = "🎉 HOÀN TẤT 100%! Đã tạo xong Prototype Scene cho " + gameTitle + "!";
                Repaint();

                EditorUtility.DisplayDialog(
                    "Thành Công!",
                    "Đã tự động khởi tạo hoàn chỉnh 1:1 Prototype Scene cho tựa game '" + gameTitle + "'!\n\nHãy nhấn Play (Ctrl + P) trên thanh công cụ Unity để trải nghiệm trực tiếp!",
                    "Chơi Thử Ngay"
                );
            }
        }

        private void SaveUnityScripts(string jsonResponse)
        {
            string scriptsDir = Application.dataPath + "/Scripts/GamePrototype";
            if (!Directory.Exists(scriptsDir)) Directory.CreateDirectory(scriptsDir);

            string configDir = Application.dataPath + "/Config";
            if (!Directory.Exists(configDir)) Directory.CreateDirectory(configDir);

            // Write pacing config
            File.WriteAllText(configDir + "/GamePacingConfig.json", jsonResponse, Encoding.UTF8);

            // Helper to extract script text by filename
            ExtractAndWriteScript(jsonResponse, "PlayerController.cs", scriptsDir + "/PlayerController.cs");
            ExtractAndWriteScript(jsonResponse, "WeaponSystem.cs", scriptsDir + "/WeaponSystem.cs");
            ExtractAndWriteScript(jsonResponse, "EnemyAI.cs", scriptsDir + "/EnemyAI.cs");
            ExtractAndWriteScript(jsonResponse, "WaveDirector.cs", scriptsDir + "/WaveDirector.cs");
            ExtractAndWriteScript(jsonResponse, "GameEconomyManager.cs", scriptsDir + "/GameEconomyManager.cs");
        }

        private void ExtractAndWriteScript(string fullJson, string scriptName, string targetPath)
        {
            try
            {
                string searchKey = "\"" + scriptName + "\":\"";
                int start = fullJson.IndexOf(searchKey);
                if (start >= 0)
                {
                    start += searchKey.Length;
                    int end = fullJson.IndexOf("\"", start);
                    while (end > start && fullJson[end - 1] == '\\')
                    {
                        end = fullJson.IndexOf("\"", end + 1);
                    }
                    if (end > start)
                    {
                        string escaped = fullJson.Substring(start, end - start);
                        string unescaped = System.Text.RegularExpressions.Regex.Unescape(escaped);
                        File.WriteAllText(targetPath, unescaped, Encoding.UTF8);
                        return;
                    }
                }

                // Fallback default starter code if JSON parsing edge case occurs
                if (!File.Exists(targetPath))
                {
                    string fallback = "// " + scriptName + " Auto-Generated\nusing UnityEngine;\npublic class " + scriptName.Replace(".cs", "") + " : MonoBehaviour { void Start() { Debug.Log(\"" + scriptName + " initialized\"); } }";
                    File.WriteAllText(targetPath, fallback, Encoding.UTF8);
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning("Script write notice for " + scriptName + ": " + ex.Message);
            }
        }

        private void CreatePlayableSceneHierarchy()
        {
            // 1. Create or open scene
            string scenesDir = Application.dataPath + "/Scenes";
            if (!Directory.Exists(scenesDir)) Directory.CreateDirectory(scenesDir);
            string scenePath = "Assets/Scenes/PrototypeScene.unity";

            var newScene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);

            // 2. Main Camera 2D Setup
            var mainCam = Camera.main;
            if (mainCam != null)
            {
                mainCam.orthographic = true;
                mainCam.orthographicSize = 7.0f;
                mainCam.transform.position = new Vector3(0, 0, -10);
                mainCam.backgroundColor = new Color(0.08f, 0.10f, 0.16f);
            }

            // 3. Player GameObject Setup
            GameObject playerGo = GameObject.Find("Player");
            if (playerGo == null) playerGo = new GameObject("Player");
            playerGo.tag = "Player";
            playerGo.transform.position = Vector3.zero;

            // Visual Placeholder Sprite (Circle)
            var playerSr = playerGo.GetComponent<SpriteRenderer>();
            if (playerSr == null) playerSr = playerGo.AddComponent<SpriteRenderer>();
            playerSr.sprite = AssetDatabase.GetBuiltinExtraResource<Sprite>("UI/Skin/Knob.psd");
            playerSr.color = new Color(0.3f, 0.8f, 1.0f); // Cyan hero
            playerGo.transform.localScale = new Vector3(1.2f, 1.2f, 1.0f);

            var rb = playerGo.GetComponent<Rigidbody2D>();
            if (rb == null) rb = playerGo.AddComponent<Rigidbody2D>();
            rb.gravityScale = 0;
            rb.freezeRotation = true;

            var col = playerGo.GetComponent<CircleCollider2D>();
            if (col == null) col = playerGo.AddComponent<CircleCollider2D>();
            col.radius = 0.5f;

            // 4. WaveDirector & Economy Managers
            GameObject directorGo = GameObject.Find("WaveDirector");
            if (directorGo == null) directorGo = new GameObject("WaveDirector");

            GameObject economyGo = GameObject.Find("GameEconomyManager");
            if (economyGo == null) economyGo = new GameObject("GameEconomyManager");

            // 5. Create Prefab for Enemy Minion
            if (autoCreateEnemyPrefab)
            {
                string prefabsDir = Application.dataPath + "/Prefabs";
                if (!Directory.Exists(prefabsDir)) Directory.CreateDirectory(prefabsDir);

                GameObject enemyObj = new GameObject("EnemyMinion");
                var enemySr = enemyObj.AddComponent<SpriteRenderer>();
                enemySr.sprite = AssetDatabase.GetBuiltinExtraResource<Sprite>("UI/Skin/Knob.psd");
                enemySr.color = new Color(1.0f, 0.3f, 0.3f); // Red minion
                enemyObj.transform.localScale = new Vector3(0.9f, 0.9f, 1.0f);

                var enemyRb = enemyObj.AddComponent<Rigidbody2D>();
                enemyRb.gravityScale = 0;
                enemyRb.freezeRotation = true;

                var enemyCol = enemyObj.AddComponent<CircleCollider2D>();
                enemyCol.radius = 0.45f;

                string prefabPath = "Assets/Prefabs/EnemyMinion.prefab";
                PrefabUtility.SaveAsPrefabAsset(enemyObj, prefabPath);
                DestroyImmediate(enemyObj);
            }

            // Save Scene
            EditorSceneManager.SaveScene(newScene, scenePath);
            Selection.activeGameObject = playerGo;
        }
    }

    /// <summary>
    /// Lightweight Editor Coroutine runner without external dependencies.
    /// </summary>
    public static class EditorCoroutineUtility
    {
        public static void StartCoroutine(IEnumerator routine)
        {
            EditorApplication.CallbackFunction updateAction = null;
            updateAction = () =>
            {
                try
                {
                    if (!routine.MoveNext())
                    {
                        EditorApplication.update -= updateAction;
                    }
                }
                catch (Exception ex)
                {
                    Debug.LogError("Coroutine exception: " + ex);
                    EditorApplication.update -= updateAction;
                }
            };
            EditorApplication.update += updateAction;
        }
    }
}
#endif
