import pytest
import time
import numpy as np
import psutil
import os
from tetris.env import TetrisEnv
from tetris.core import TetrisBoard, Action
import threading
from concurrent.futures import ThreadPoolExecutor


class TestPerformanceMetrics:
    """パフォーマンス測定テスト"""

    def test_step_execution_speed(self, tetris_env):
        """ステップ実行速度テスト"""
        observation, info = tetris_env.reset()
        
        # ウォームアップ
        for _ in range(10):
            tetris_env.step(Action.NOTHING)
        
        # 実際の測定
        start_time = time.perf_counter()
        step_count = 1000
        
        for i in range(step_count):
            action = i % 6
            obs, reward, terminated, truncated, info = tetris_env.step(action)
            if terminated:
                observation, info = tetris_env.reset()
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        fps = step_count / execution_time
        
        print(f"Performance: {fps:.2f} FPS ({step_count} steps in {execution_time:.3f}s)")
        
        # 目標: 60FPS以上
        assert fps >= 60, f"Performance below target: {fps:.2f} FPS < 60 FPS"

    def test_memory_usage_stability(self, tetris_env):
        """メモリ使用量安定性テスト"""
        process = psutil.Process(os.getpid())
        
        # 初期メモリ使用量
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 大量ステップ実行
        observation, info = tetris_env.reset()
        for i in range(5000):
            action = i % 6
            obs, reward, terminated, truncated, info = tetris_env.step(action)
            if terminated:
                observation, info = tetris_env.reset()
            
            # 1000ステップごとにメモリをチェック
            if i % 1000 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                print(f"Step {i}: Memory usage: {current_memory:.2f}MB (+{memory_increase:.2f}MB)")
        
        # 最終メモリ使用量
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        print(f"Total memory increase: {memory_increase:.2f}MB")
        
        # 目標: メモリ増加50MB以下
        assert memory_increase < 50, f"Memory leak detected: {memory_increase:.2f}MB increase"

    def test_rendering_performance(self, tetris_env):
        """レンダリング性能テスト"""
        observation, info = tetris_env.reset()
        
        render_times = []
        render_count = 100
        
        for _ in range(render_count):
            start_time = time.perf_counter()
            render_output = tetris_env.render()
            end_time = time.perf_counter()
            
            render_time = (end_time - start_time) * 1000  # ms
            render_times.append(render_time)
        
        avg_render_time = np.mean(render_times)
        max_render_time = np.max(render_times)
        
        print(f"Rendering performance: avg={avg_render_time:.2f}ms, max={max_render_time:.2f}ms")
        
        # 目標: 平均16ms以下（60FPS相当）
        assert avg_render_time <= 16, f"Rendering too slow: {avg_render_time:.2f}ms > 16ms"
        assert max_render_time <= 33, f"Max rendering time too slow: {max_render_time:.2f}ms > 33ms"

    def test_environment_initialization_speed(self):
        """環境初期化速度テスト"""
        init_times = []
        init_count = 50
        
        for _ in range(init_count):
            start_time = time.perf_counter()
            env = TetrisEnv()
            env.reset()
            end_time = time.perf_counter()
            
            init_time = (end_time - start_time) * 1000  # ms
            init_times.append(init_time)
            env.close()
        
        avg_init_time = np.mean(init_times)
        max_init_time = np.max(init_times)
        
        print(f"Initialization performance: avg={avg_init_time:.2f}ms, max={max_init_time:.2f}ms")
        
        # 目標: 平均100ms以下
        assert avg_init_time <= 100, f"Initialization too slow: {avg_init_time:.2f}ms > 100ms"

    def test_board_computation_performance(self, tetris_board):
        """ボード計算パフォーマンステスト"""
        tetris_board.spawn_piece()
        
        # get_board_with_piece()の性能測定
        computation_times = []
        computation_count = 1000
        
        for _ in range(computation_count):
            start_time = time.perf_counter()
            board_with_piece = tetris_board.get_board_with_piece()
            end_time = time.perf_counter()
            
            computation_time = (end_time - start_time) * 1000  # ms
            computation_times.append(computation_time)
        
        avg_computation_time = np.mean(computation_times)
        max_computation_time = np.max(computation_times)
        
        print(f"Board computation: avg={avg_computation_time:.3f}ms, max={max_computation_time:.3f}ms")
        
        # 目標: 平均1ms以下
        assert avg_computation_time <= 1.0, f"Board computation too slow: {avg_computation_time:.3f}ms > 1ms"

    def test_action_processing_latency(self, tetris_env):
        """アクション処理レイテンシテスト"""
        observation, info = tetris_env.reset()
        
        action_latencies = {action: [] for action in range(6)}
        
        # 各アクションを100回ずつテスト
        for action in range(6):
            for _ in range(100):
                start_time = time.perf_counter()
                obs, reward, terminated, truncated, info = tetris_env.step(action)
                end_time = time.perf_counter()
                
                latency = (end_time - start_time) * 1000  # ms
                action_latencies[action].append(latency)
                
                if terminated:
                    observation, info = tetris_env.reset()
        
        # 各アクションのレイテンシを確認
        for action, latencies in action_latencies.items():
            avg_latency = np.mean(latencies)
            max_latency = np.max(latencies)
            
            print(f"Action {action}: avg={avg_latency:.3f}ms, max={max_latency:.3f}ms")
            
            # 目標: 平均5ms以下
            assert avg_latency <= 5.0, f"Action {action} too slow: {avg_latency:.3f}ms > 5ms"

    @pytest.mark.slow
    def test_long_running_stability(self, tetris_env):
        """長時間実行安定性テスト"""
        observation, info = tetris_env.reset()
        
        start_time = time.time()
        target_duration = 60  # 60秒間実行
        step_count = 0
        reset_count = 0
        
        while time.time() - start_time < target_duration:
            action = np.random.randint(0, 6)
            obs, reward, terminated, truncated, info = tetris_env.step(action)
            step_count += 1
            
            if terminated:
                observation, info = tetris_env.reset()
                reset_count += 1
        
        execution_time = time.time() - start_time
        avg_fps = step_count / execution_time
        
        print(f"Long run: {step_count} steps, {reset_count} resets in {execution_time:.1f}s")
        print(f"Average FPS: {avg_fps:.2f}")
        
        # 安定性確認
        assert avg_fps >= 30, f"Performance degraded during long run: {avg_fps:.2f} FPS"
        assert reset_count > 0, "No game overs occurred during long run (suspicious)"

    def test_concurrent_environment_performance(self):
        """並行環境パフォーマンステスト"""
        num_environments = 4
        steps_per_env = 1000
        
        def run_environment(env_id):
            env = TetrisEnv()
            try:
                start_time = time.perf_counter()
                observation, info = env.reset()
                
                for i in range(steps_per_env):
                    action = i % 6
                    obs, reward, terminated, truncated, info = env.step(action)
                    if terminated:
                        observation, info = env.reset()
                
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                fps = steps_per_env / execution_time
                
                return env_id, fps, execution_time
            finally:
                env.close()
        
        # 並行実行
        start_time = time.perf_counter()
        with ThreadPoolExecutor(max_workers=num_environments) as executor:
            futures = [executor.submit(run_environment, i) for i in range(num_environments)]
            results = [future.result() for future in futures]
        end_time = time.perf_counter()
        
        total_execution_time = end_time - start_time
        
        # 結果分析
        for env_id, fps, exec_time in results:
            print(f"Environment {env_id}: {fps:.2f} FPS ({exec_time:.3f}s)")
            
            # 各環境が最低30FPSを維持
            assert fps >= 30, f"Environment {env_id} performance: {fps:.2f} FPS < 30 FPS"
        
        # 並行実行効率確認
        sequential_time = sum(exec_time for _, _, exec_time in results)
        parallel_efficiency = sequential_time / total_execution_time
        
        print(f"Parallel efficiency: {parallel_efficiency:.2f}x")
        
        # 並行実行により少なくとも2倍の効率向上を期待
        assert parallel_efficiency >= 2.0, f"Poor parallel efficiency: {parallel_efficiency:.2f}x"


class TestScalabilityLimits:
    """スケーラビリティ限界テスト"""

    def test_maximum_simultaneous_environments(self):
        """最大同時環境数テスト"""
        max_envs = 20
        envs = []
        successful_envs = 0
        
        try:
            for i in range(max_envs):
                try:
                    env = TetrisEnv()
                    observation, info = env.reset()
                    envs.append(env)
                    successful_envs += 1
                except Exception as e:
                    print(f"Failed to create environment {i}: {e}")
                    break
            
            print(f"Successfully created {successful_envs} environments")
            
            # 最低10環境は作成できるべき
            assert successful_envs >= 10, f"Too few environments created: {successful_envs} < 10"
            
            # すべての環境が動作することを確認
            for i, env in enumerate(envs):
                obs, reward, terminated, truncated, info = env.step(Action.NOTHING)
                assert isinstance(obs, dict), f"Environment {i} returned invalid observation"
        
        finally:
            # クリーンアップ
            for env in envs:
                try:
                    env.close()
                except:
                    pass

    def test_memory_scaling_with_environments(self):
        """環境数に対するメモリスケーリングテスト"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        env_counts = [1, 2, 4, 8]
        memory_usage = []
        
        for count in env_counts:
            envs = []
            try:
                # 指定数の環境を作成
                for _ in range(count):
                    env = TetrisEnv()
                    env.reset()
                    envs.append(env)
                
                # メモリ使用量測定
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_per_env = (current_memory - initial_memory) / count
                memory_usage.append((count, current_memory - initial_memory, memory_per_env))
                
                print(f"{count} environments: {current_memory - initial_memory:.2f}MB total, "
                      f"{memory_per_env:.2f}MB per env")
                
            finally:
                # クリーンアップ
                for env in envs:
                    env.close()
        
        # メモリ使用量の線形性を確認
        # 環境数が倍になっても、1環境あたりのメモリ使用量は大きく変わらないはず
        if len(memory_usage) >= 2:
            first_per_env = memory_usage[0][2]
            last_per_env = memory_usage[-1][2]
            
            # 1環境あたりのメモリ使用量が2倍を超えないことを確認
            memory_ratio = last_per_env / first_per_env if first_per_env > 0 else 1
            assert memory_ratio <= 2.0, f"Memory scaling issue: {memory_ratio:.2f}x increase per env"

    @pytest.mark.timeout(30)
    def test_stress_test_rapid_resets(self, tetris_env):
        """高速リセットストレステスト"""
        reset_count = 1000
        start_time = time.perf_counter()
        
        for i in range(reset_count):
            observation, info = tetris_env.reset()
            # 少しステップを実行してからリセット
            for _ in range(5):
                obs, reward, terminated, truncated, info = tetris_env.step(i % 6)
                if terminated:
                    break
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        resets_per_second = reset_count / execution_time
        
        print(f"Reset performance: {resets_per_second:.2f} resets/second")
        
        # 目標: 毎秒100回以上のリセット
        assert resets_per_second >= 100, f"Reset performance: {resets_per_second:.2f} < 100 resets/second"

    def test_cpu_usage_monitoring(self, tetris_env):
        """CPU使用率監視テスト"""
        import threading
        
        cpu_usage_samples = []
        monitoring = True
        
        def monitor_cpu():
            while monitoring:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_usage_samples.append(cpu_percent)
        
        # CPU監視開始
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()
        
        try:
            # 負荷をかける
            observation, info = tetris_env.reset()
            for i in range(2000):
                action = i % 6
                obs, reward, terminated, truncated, info = tetris_env.step(action)
                if terminated:
                    observation, info = tetris_env.reset()
        
        finally:
            # 監視停止
            monitoring = False
            monitor_thread.join()
        
        if cpu_usage_samples:
            avg_cpu = np.mean(cpu_usage_samples)
            max_cpu = np.max(cpu_usage_samples)
            
            print(f"CPU usage: avg={avg_cpu:.1f}%, max={max_cpu:.1f}%")
            
            # CPU使用率が極端に高くないことを確認
            assert max_cpu <= 90, f"CPU usage too high: {max_cpu:.1f}% > 90%"