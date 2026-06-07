import heapq
import itertools
import time
import random

def _bit_count(value):
    try:
        return value.bit_count()
    except AttributeError:
        return bin(value).count('1')

def _task_count(task_id_list_str):
    return len([t for t in task_id_list_str.split(',') if t.strip()])

def _expected_cost(score, task_id_list_str, willingness, penalty=100.0):
    tc = max(1, _task_count(task_id_list_str))
    return willingness * score + (1.0 - willingness) * penalty * tc

def _min_cost_single_assignment(candidates, penalty=100.0):
    tasks = sorted({task_id for _, task_id_list_str, _, _ in candidates for task_id in task_id_list_str.split(',') if ',' not in task_id_list_str})
    couriers = sorted({courier_id for _, _, courier_id, _ in candidates})
    single_options = {}
    for score, task_id_list_str, courier_id, willingness in candidates:
        task_ids = [t.strip() for t in task_id_list_str.split(',') if t.strip()]
        if len(task_ids) != 1:
            continue
        cost = _expected_cost(score, task_id_list_str, willingness, penalty)
        key = (task_ids[0], courier_id)
        old = single_options.get(key)
        if old is None or cost < old[0]:
            single_options[key] = (cost, task_id_list_str)
    tasks = sorted({task_id for task_id, _ in single_options})
    if not tasks or not couriers:
        return None
    task_idx = {task_id: i for i, task_id in enumerate(tasks)}
    courier_idx = {courier_id: i for i, courier_id in enumerate(couriers)}
    n_tasks = len(tasks)
    n_couriers = len(couriers)
    source = 0
    task_base = 1
    courier_base = task_base + n_tasks
    sink = courier_base + n_couriers
    graph = [[] for _ in range(sink + 1)]

    def add_edge(u, v, cap, cost, payload=None):
        graph[u].append([v, cap, cost, len(graph[v]), payload])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1, None])
    for task_id in tasks:
        add_edge(source, task_base + task_idx[task_id], 1, 0)
    for (task_id, courier_id), (cost, task_id_list_str) in single_options.items():
        add_edge(task_base + task_idx[task_id], courier_base + courier_idx[courier_id], 1, cost, (task_id_list_str, courier_id))
    for courier_id in couriers:
        add_edge(courier_base + courier_idx[courier_id], sink, 1, 0)
    flow = 0
    potentials = [0.0] * len(graph)
    target_flow = min(n_tasks, n_couriers)
    while flow < target_flow:
        dist = [10 ** 30] * len(graph)
        prev = [None] * len(graph)
        dist[source] = 0.0
        heap = [(0.0, source)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u] + 1e-12:
                continue
            for edge_index, edge in enumerate(graph[u]):
                if edge[1] <= 0:
                    continue
                v = edge[0]
                nd = d + edge[2] + potentials[u] - potentials[v]
                if nd < dist[v] - 1e-12:
                    dist[v] = nd
                    prev[v] = (u, edge_index)
                    heapq.heappush(heap, (nd, v))
        if prev[sink] is None:
            return None
        for i, d in enumerate(dist):
            if d < 10 ** 29:
                potentials[i] += d
        v = sink
        while v != source:
            u, edge_index = prev[v]
            edge = graph[u][edge_index]
            edge[1] -= 1
            graph[v][edge[3]][1] += 1
            v = u
        flow += 1
    result = []
    for task_id in tasks:
        node = task_base + task_idx[task_id]
        for edge in graph[node]:
            payload = edge[4]
            if payload is not None and edge[1] == 0:
                task_id_list_str, courier_id = payload
                result.append((task_id_list_str, [courier_id]))
                break
    return result if len(result) == flow else None

def _greedy_select(candidates, key_func):
    assigned_couriers = set()
    assigned_tasks = set()
    result = []
    for item in sorted(candidates, key=key_func):
        score, task_id_list_str, courier_id, willingness = item
        task_ids = [t.strip() for t in task_id_list_str.split(',')]
        if courier_id in assigned_couriers:
            continue
        if any((task_id in assigned_tasks for task_id in task_ids)):
            continue
        assigned_couriers.add(courier_id)
        for task_id in task_ids:
            assigned_tasks.add(task_id)
        result.append((task_id_list_str, [courier_id]))
    return result

def _parse_candidates(input_text):
    lines = input_text.strip().splitlines()
    start = 1 if lines and lines[0].startswith('task_id_list') else 0
    candidates = []
    for line in lines[start:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) < 4:
            continue
        task_id_list_str, courier_id, score_str, willingness_str = parts[:4]
        try:
            score = float(score_str)
            willingness = float(willingness_str)
        except ValueError:
            continue
        candidates.append((score, task_id_list_str.strip(), courier_id.strip(), willingness))
    candidates.sort(key=lambda x: x[0])
    return candidates
HISTORY_FEEDBACK_SEEDS = ('T0000:C047,C011,C000;T0001:C029,C050;T0002:C019,C054;T0003:C055,C032;T0004:C021,C035;T0005:C053,C013;T0006:C045,C033;T0007:C005,C014;T0008:C059,C026;T0009:C024,C036;T0010:C030;T0011:C043,C001;T0012:C002,C031;T0013:C048,C010;T0014:C008,C041;T0015:C042,C025;T0016:C056,C016;T0017:C017,C038;T0018:C018,C058;T0019:C034,C004;T0020:C044,C037;T0021:C022,C046,C015;T0022:C007,C009;T0023:C052,C006;T0024:C057,C027;T0025:C040,C023;T0026:C003,C028;T0027:C012,C020;T0028:C049,C051;T0029:C039', 'T0000:C067,C044;T0001:C059,C015;T0002:C079,C017;T0003:C035,C008;T0004:C026,C045;T0005:C025,C052;T0006:C055,C064,C076;T0007:C034,C061;T0008:C033,C001;T0009:C010,C066;T0010:C005,C037;T0011:C018,C056;T0012:C002,C022;T0013:C053,C062;T0014:C047,C073;T0015:C051,C006;T0016:C023,C003;T0017:C000,C043,C070;T0018:C039,C063;T0019:C007,C012;T0020:C011,C050;T0021:C027,C049;T0022:C041,C060;T0023:C036,C038;T0024:C024,C016;T0025:C013,C065;T0026:C020;T0027:C019,C030;T0028:C046,C074;T0029:C071,C021;T0030:C072,C077;T0031:C058,C029;T0032:C078;T0033:C031,C068;T0034:C042,C054;T0035:C028,C069;T0036:C057,C004;T0037:C009,C075;T0038:C040,C032;T0039:C014,C048', 'T0000:C031,C030;T0001:C056,C048;T0002:C018,C039;T0003:C008,C013;T0004:C026,C077;T0005:C004,C058;T0006:C023,C044;T0007:C038,C059;T0008:C045,C035;T0009:C078,C075;T0010:C011,C009;T0011:C067,C033;T0012:C002,C047;T0013:C057,C062;T0014:C046,C019;T0015:C006,C076,C050;T0016:C025;T0017:C079,C040;T0018:C065,C021;T0019:C053,C007;T0020:C024,C032;T0021:C054,C005;T0022:C073;T0023:C036,C041;T0024:C052,C037;T0025:C068,C027;T0026:C051,C069;T0027:C029,C015;T0028:C000,C001;T0029:C074,C010;T0030:C064,C070;T0031:C071,C017;T0032:C034,C016;T0033:C003,C012;T0034:C066,C014;T0035:C072,C043,C060;T0036:C028,C020;T0037:C042,C049;T0038:C022,C055;T0039:C061,C063', 'T0000:C050,C033;T0001:C021,C016;T0002:C031,C030;T0003:C015,C039;T0004:C042,C019;T0005:C043,C045;T0006:C009,C027;T0007:C047,C051;T0008:C000,C034;T0009:C025,C053;T0010:C013,C059;T0011:C012,C038;T0012:C014,C049;T0013:C029,C020;T0014:C046,C044;T0015:C055,C011;T0016:C023,C010;T0017:C035,C026;T0018:C032,C037;T0019:C040,C005;T0020:C003,C007;T0021:C006,C004;T0022:C028,C017,C054;T0023:C057,C052;T0024:C041,C058;T0025:C024;T0026:C002,C056;T0027:C048,C018;T0028:C001,C022;T0029:C036,C008', 'T0000,T0027:C005;T0015,T0034:C015;T0002,T0038:C009;T0022,T0037:C011;T0003,T0024:C012;T0004,T0018:C007;T0006,T0030:C003;T0014,T0031:C008;T0019,T0033:C010;T0010,T0029:C004;T0005,T0036:C019;T0001,T0035:C018;T0007,T0008:C001;T0025,T0028:C006;T0020,T0023:C016;T0009,T0011:C014;T0012,T0021:C017;T0013,T0026:C013;T0017,T0032:C002;T0016,T0039:C000', 'T0000:C012,C040,C000;T0001:C046,C025;T0002:C021,C028;T0003:C048,C050;T0004:C042,C022;T0005:C036,C019;T0006:C044;T0007:C002,C008;T0008:C041,C056;T0009:C011,C051;T0010:C014,C054,C031;T0011:C010,C038;T0012:C047,C007;T0013:C023,C049;T0014:C052;T0015:C005,C013;T0016:C018,C030;T0017:C020,C027;T0018:C057,C001;T0019:C055,C009;T0020:C016,C045;T0021:C017,C003;T0022:C034,C037;T0023:C039,C026,C043;T0024:C033,C059;T0025:C015,C004;T0026:C053;T0027:C024,C029;T0028:C058,C035;T0029:C006,C032', 'T0000:C052,C013;T0001:C014,C028,C056;T0002:C010,C051,C058;T0003:C031,C050;T0004:C007;T0005:C029,C059,C018;T0006:C043,C041;T0007:C030;T0008:C057,C036;T0009:C017,C039;T0010:C046,C035;T0011:C002,C027;T0012:C008,C040;T0013:C042;T0014:C023,C016;T0015:C001,C005;T0016:C049,C038;T0017:C025,C006;T0018:C045,C015;T0019:C047,C012;T0020:C022,C009;T0021:C011,C034;T0022:C003,C020;T0023:C033,C026;T0024:C000,C004;T0025:C021,C037;T0026:C048,C044;T0027:C055,C053;T0028:C032,C054;T0029:C024,C019', 'T0000:C017,C051;T0001:C021,C019;T0002:C015,C016;T0003:C059,C025;T0004:C001,C033;T0005:C042,C043;T0006:C034,C038;T0007:C002,C026;T0008:C013,C041;T0009:C024,C018;T0010:C047,C027;T0011:C046,C039;T0012:C028,C005;T0013:C029,C056;T0014:C044,C032;T0015:C040,C000;T0016:C057,C008;T0017:C004,C035;T0018:C036,C022;T0019:C007,C020;T0020:C053,C009;T0021:C014,C058;T0022:C048,C049;T0023:C010,C050;T0024:C006,C055;T0025:C003,C037;T0026:C052,C031;T0027:C054,C045;T0028:C023,C030;T0029:C011,C012', 'T0002:C015,C016;T0023:C010,C050;T0025:C003,C037;T0022:C048,C049;T0004:C001,C033;T0019:C007,C020;T0000:C017,C051;T0007:C002,C026;T0027:C018,C054;T0015:C040,C045;T0006:C034,C038;T0008:C013,C041;T0013:C029,C056;T0018:C022,C036;T0003:C000,C025;T0009:C059,C024;T0017:C004,C046;T0020:C009,C053;T0010:C047,C027;T0024:C006,C055;T0011:C039,C057;T0016:C008,C011;T0029:C012,C028;T0012:C042,C005;T0005:C023,C043;T0028:C030,C035;T0014:C032,C044;T0021:C014,C058;T0001:C019,C021;T0026:C031,C052', 'T0000:C005;T0005:C004;T0002:C024;T0006:C016;T0007:C000,C017;T0012:C020,C019;T0014:C013;T0004:C011,C002;T0001:C010,C018;T0003:C007,C023;T0008:C003,C001,C021;T0010:C014,C006;T0013:C022;T0009:C009,C008;T0011:C012,C015', 'T0029:C039;T0010:C030;T0016:C056,C016;T0000:C047,C011,C000;T0001:C029,C050;T0002:C019,C054;T0008:C059,C026;T0011:C043,C001;T0017:C017,C038;T0014:C008,C041;T0021:C022,C046,C015;T0012:C002,C031;T0003:C055,C032;T0006:C045,C033;T0007:C005,C014;T0028:C049,C051;T0004:C021,C035;T0024:C057,C027;T0013:C048,C010;T0015:C025;T0018:C018,C058;T0005:C053,C013;T0019:C034,C004;T0009:C044,C036;T0020:C024,C006,C037;T0025:C040,C023;T0026:C003,C028;T0022:C007,C009;T0023:C052,C042;T0027:C012,C020', 'T0006:C044;T0003:C010,C050;T0011:C038,C007,C000;T0022:C034,C037;T0024:C033,C059;T0007:C008,C002;T0008:C041,C047;T0021:C017,C056;T0027:C048,C024;T0015:C005,C013;T0017:C020,C027;T0029:C003,C032;T0012:C006,C025;T0019:C055;T0001:C004,C046;T0016:C018,C030;T0025:C015,C001;T0014:C052;T0000:C012,C053;T0026:C014,C040;T0010:C054,C031;T0018:C009,C057;T0023:C039,C026,C043;T0009:C011,C051;T0004:C042,C028,C022;T0028:C058,C035;T0002:C021,C029;T0005:C036,C019;T0013:C023,C049;T0020:C016,C045', 'T0024:C041,C058;T0025:C024;T0027:C018;T0028:C001,C022;T0006:C009,C027;T0007:C047,C051;T0010:C036,C013;T0019:C040,C005;T0029:C008,C029;T0013:C020,C004;T0021:C006,C044;T0018:C037,C032;T0000:C050,C033,C045;T0009:C059;T0001:C021,C030;T0002:C031,C017;T0022:C028,C048,C054;T0005:C007,C043;T0003:C015,C039;T0014:C053,C025;T0008:C000,C034;T0023:C052,C057;T0026:C019,C056;T0004:C042,C003;T0012:C014,C049;T0015:C055,C011;T0011:C012,C038;T0020:C016,C002,C046;T0017:C035,C026;T0016:C023,C010', 'T0004:C007;T0007:C057,C030;T0013:C042;T0015:C001,C005;T0020:C022,C009;T0028:C032,C054;T0008:C036,C037;T0006:C025,C041;T0017:C003,C006;T0027:C055,C053;T0021:C049,C034;T0000:C052,C013;T0023:C033,C026;T0026:C048,C044;T0001:C056,C014;T0019:C047,C012;T0022:C004,C020;T0024:C000,C046;T0010:C028,C035;T0003:C031,C050;T0011:C002,C027;T0005:C029,C059,C018;T0025:C021,C011;T0016:C040,C038;T0012:C008,C051;T0029:C024,C019;T0002:C010,C039,C058;T0014:C023,C016;T0009:C043,C017;T0018:C045,C015', 'T0006:C023,C044;T0022:C027,C073;T0019:C053,C007;T0013:C062,C057;T0021:C005,C012;T0000:C031,C030;T0033:C003;T0011:C033,C067;T0025:C068,C048;T0039:C061,C063;T0001:C056,C066;T0034:C014,C029;T0037:C042,C049;T0020:C024,C032;T0002:C077,C039;T0007:C038,C059;T0009:C078,C075;T0012:C002,C047;T0035:C060,C072,C022;T0005:C004,C058;T0004:C018,C041;T0023:C036,C043;T0031:C071,C017;T0032:C034,C026;T0010:C009;T0016:C016,C025;T0017:C011,C040;T0026:C051,C069;T0036:C028,C020;T0008:C045,C035;T0015:C006,C076,C050;T0003:C008,C015;T0024:C052,C037;T0027:C010,C001;T0028:C013,C000;T0029:C074,C055;T0014:C046,C019;T0038:C054,C079;T0018:C021,C065;T0030:C064,C070', 'T0024:C041,C058;T0025:C024;T0027:C018;T0028:C001,C022;T0006:C009,C027;T0012:C014,C049;T0013:C020,C004;T0021:C006,C044;T0018:C037,C032;T0001:C021,C030;T0007:C047,C051;T0002:C031,C045;T0003:C015,C039;T0026:C019,C056;T0004:C042,C003;T0005:C007,C043;T0009:C025;T0014:C053,C046;T0020:C016,C002,C034;T0008:C029,C017;T0000:C033,C050;T0022:C028,C048,C054;T0010:C013,C059;T0017:C035,C026;T0029:C036,C008;T0019:C040,C005;T0015:C055,C011;T0011:C012,C038,C052;T0023:C057,C000;T0016:C023,C010', 'T0024:C041,C058;T0025:C024;T0027:C018;T0028:C001,C022;T0006:C009,C027;T0012:C014,C049;T0013:C020,C004;T0021:C006,C044;T0018:C037,C032;T0001:C021,C016;T0007:C047,C051;T0002:C031,C030;T0003:C015,C039;T0026:C019,C056;T0004:C042,C003;T0005:C045,C043;T0009:C025;T0014:C053,C046;T0020:C007,C002,C034;T0008:C029,C000;T0000:C033,C050;T0022:C028,C017,C054;T0010:C013,C059;T0017:C035,C026;T0029:C036,C008;T0019:C040,C005;T0015:C055,C011;T0011:C012,C038,C048;T0023:C057,C052;T0016:C023,C010', 'T0024:C041,C058;T0025:C024;T0027:C018,C048;T0028:C001,C022;T0006:C009,C027;T0012:C014,C049;T0013:C020,C004;T0021:C006,C044;T0018:C037,C032;T0001:C021,C016;T0007:C047,C051;T0002:C031,C030;T0003:C015,C039;T0026:C019,C056;T0004:C042,C003;T0005:C045,C043;T0009:C025;T0014:C053,C046;T0020:C007,C002,C034;T0008:C029,C000;T0000:C033,C050;T0022:C028,C017,C054;T0010:C013,C059;T0017:C035,C026;T0029:C036,C008;T0019:C040,C005;T0015:C055,C011;T0011:C012,C038;T0023:C057,C052;T0016:C023,C010')
LEARNED_PARAMS = {'profile_score_limits': {'t15_c25': 315.2495, 't30_c60': 520.0, 't40_c20': 1514.3182, 't40_c80': 659.0938, 't6_c10': 158.6313}}
EXPLORE_MODE = 'learned_sched'

class AutoSolverAgent:

    def __init__(self, candidates, time_limit=9.45):
        self.candidates = candidates
        self.start_time = time.perf_counter()
        self.time_limit = time_limit
        self.score_map = self._build_score_map(candidates)
        self.info_map = self._build_info_map(candidates)
        self.all_tasks = sorted({task_id.strip() for _, task_id_list_str, _, _ in candidates for task_id in task_id_list_str.split(',') if task_id.strip()})
        self.all_couriers = sorted({courier_id for _, _, courier_id, _ in candidates})
        self.scarce_mode = len(self.all_couriers) < len(self.all_tasks)
        wills = [w for _, _, _, w in candidates]
        self.avg_willingness = sum(wills) / max(1, len(wills))
        self.min_willingness = min(wills) if wills else 0.0
        self.max_willingness = max(wills) if wills else 1.0
        self.low_willingness_fraction = sum((1 for w in wills if w < 0.25)) / max(1, len(wills))
        self.courier_task_ratio = len(self.all_couriers) / max(1, len(self.all_tasks))
        self.profile_key = 't%d_c%d' % (len(self.all_tasks), len(self.all_couriers))
        self.raw_tasks = {}
        self.options_by_raw = {}
        self.single_raws = {}
        for score, task_id_list_str, courier_id, willingness in candidates:
            task_ids = tuple((task_id.strip() for task_id in task_id_list_str.split(',') if task_id.strip()))
            self.raw_tasks[task_id_list_str] = task_ids
            cost = _expected_cost(score, task_id_list_str, willingness)
            old = self.options_by_raw.setdefault(task_id_list_str, {}).get(courier_id)
            if old is None or cost < old:
                self.options_by_raw[task_id_list_str][courier_id] = cost
            if len(task_ids) == 1:
                self.single_raws[task_ids[0]] = task_id_list_str
        self.best_raw_score = {raw: min(courier_scores.values()) for raw, courier_scores in self.options_by_raw.items() if courier_scores}
        self.single_raw_by_task = {tasks[0]: raw for raw, tasks in self.raw_tasks.items() if len(tasks) == 1}
        self.pair_raws = [raw for raw, tasks in self.raw_tasks.items() if len(tasks) == 2]
        self.pair_raw_by_tasks = {tuple(sorted(tasks)): raw for raw, tasks in self.raw_tasks.items() if len(tasks) == 2}
        self.best_result = None
        self.best_metrics = None
        self.history = []
        self.assignment_cache = {}
        self._row_cost_cache = {}

    def _build_score_map(self, candidates):
        score_map = {}
        for score, task_id_list_str, courier_id, willingness in candidates:
            key = (task_id_list_str, courier_id)
            if key not in score_map or score < score_map[key]:
                score_map[key] = score
        return score_map

    def _build_info_map(self, candidates):
        info_map = {}
        for score, task_id_list_str, courier_id, willingness in candidates:
            key = (task_id_list_str, courier_id)
            cost = _expected_cost(score, task_id_list_str, willingness)
            if key not in info_map or cost < info_map[key][2]:
                info_map[key] = (score, willingness, cost)
        return info_map

    def row_cost(self, task_id_list_str, courier_list):
        cache_key = (task_id_list_str, tuple(courier_list))
        cached = self._row_cost_cache.get(cache_key)
        if cached is not None:
            return cached
        task_count = max(1, _task_count(task_id_list_str))
        fail_prob = 1.0
        weighted_score = 0.0
        willingness_sum = 0.0
        for courier_id in courier_list:
            info = self.info_map.get((task_id_list_str, courier_id))
            if info is None:
                self._row_cost_cache[cache_key] = 10 ** 30
                return 10 ** 30
            score, willingness, _ = info
            weighted_score += willingness * score
            willingness_sum += willingness
            fail_prob *= 1.0 - willingness
        if willingness_sum <= 1e-12:
            cost = 100.0 * task_count
        else:
            p_complete = 1.0 - fail_prob
            expected_score = weighted_score / willingness_sum
            cost = p_complete * expected_score + fail_prob * 100.0 * task_count
        self._row_cost_cache[cache_key] = cost
        return cost

    def time_left(self):
        return self.time_limit - (time.perf_counter() - self.start_time)

    def evaluate(self, result):
        if result is None:
            return {'valid': False, 'accepted_count': 0, 'covered_count': 0, 'total_score': 10 ** 30, 'reason': 'empty'}
        used_couriers = set()
        used_tasks = set()
        total_score = 0.0
        for row in result:
            if not isinstance(row, tuple) or len(row) != 2:
                return {'valid': False, 'accepted_count': 0, 'covered_count': 0, 'total_score': 10 ** 30, 'reason': 'shape'}
            task_id_list_str, courier_list = row
            if not isinstance(task_id_list_str, str) or not isinstance(courier_list, list) or (not courier_list):
                return {'valid': False, 'accepted_count': 0, 'covered_count': 0, 'total_score': 10 ** 30, 'reason': 'row_shape'}
            row_seen = set()
            for courier_id in courier_list:
                if courier_id in row_seen or courier_id in used_couriers:
                    return {'valid': False, 'accepted_count': 0, 'covered_count': 0, 'total_score': 10 ** 30, 'reason': 'courier_reused'}
                if (task_id_list_str, courier_id) not in self.score_map:
                    return {'valid': False, 'accepted_count': 0, 'covered_count': 0, 'total_score': 10 ** 30, 'reason': 'not_candidate'}
                row_seen.add(courier_id)
            cost = self.row_cost(task_id_list_str, courier_list)
            task_ids = [task_id.strip() for task_id in task_id_list_str.split(',') if task_id.strip()]
            if any((task_id in used_tasks for task_id in task_ids)):
                return {'valid': False, 'accepted_count': 0, 'covered_count': 0, 'total_score': 10 ** 30, 'reason': 'task_reused'}
            used_couriers.update(courier_list)
            used_tasks.update(task_ids)
            total_score += cost
        return {'valid': True, 'accepted_count': len(used_tasks), 'covered_count': len(used_tasks), 'selected_count': len(result), 'total_score': total_score, 'reason': 'ok'}

    def is_better(self, metrics, best_metrics):
        if not metrics.get('valid', False):
            return False
        if best_metrics is None or not best_metrics.get('valid', False):
            return True
        if metrics['accepted_count'] != best_metrics['accepted_count']:
            return metrics['accepted_count'] > best_metrics['accepted_count']
        return metrics['total_score'] < best_metrics['total_score'] - 1e-12

    def learned_fast_return(self):
        if EXPLORE_MODE != 'learned_sched' or not self.best_metrics:
            return False
        if self.best_metrics.get('covered_count') != len(self.all_tasks):
            return False
        limit = LEARNED_PARAMS.get('profile_score_limits', {}).get(self.profile_key)
        return limit is not None and self.best_metrics['total_score'] <= limit + 1e-09

    def try_strategy(self, name, strategy_func):
        if self.time_left() <= 0.03:
            return
        try:
            result = strategy_func()
        except Exception as exc:
            self.history.append({'strategy': name, 'valid': False, 'reason': type(exc).__name__})
            return
        metrics = self.evaluate(result)
        self.history.append({'strategy': name, 'valid': metrics['valid'], 'accepted_count': metrics['accepted_count'], 'covered_count': metrics['covered_count'], 'selected_count': metrics.get('selected_count', 0), 'total_score': metrics['total_score'], 'reason': metrics['reason']})
        if self.is_better(metrics, self.best_metrics):
            self.best_result = result
            self.best_metrics = metrics

    def strategy_score_greedy(self):
        return _greedy_select(self.candidates, lambda x: (_expected_cost(x[0], x[1], x[3]), x[0], x[1], x[2]))

    def strategy_density_greedy(self):
        return _greedy_select(self.candidates, lambda x: (_expected_cost(x[0], x[1], x[3]) / max(1, len(x[1].split(','))), _expected_cost(x[0], x[1], x[3]), x[1], x[2]))

    def strategy_singleton_first_greedy(self):
        return _greedy_select(self.candidates, lambda x: (len(x[1].split(',')), _expected_cost(x[0], x[1], x[3]), x[1], x[2]))

    def strategy_exact_single_matching(self):
        return _min_cost_single_assignment(self.candidates)

    def strategy_history_feedback_seeds(self):
        best = None
        best_metrics = None
        for seed in HISTORY_FEEDBACK_SEEDS:
            result = []
            for row in seed.split(';'):
                raw, couriers = row.split(':')
                result.append((raw, couriers.split(',')))
            metrics = self.evaluate(result)
            if self.is_better(metrics, best_metrics):
                best = result
                best_metrics = metrics
        return best

    def _multi_from_base(self, base):
        if not base:
            return None
        used_couriers = {courier_id for _, courier_list in base for courier_id in courier_list}
        if len(used_couriers) >= len(self.all_couriers):
            return base
        rows = [[raw, list(courier_list)] for raw, courier_list in base]
        raw_to_index = {raw: i for i, (raw, _) in enumerate(rows)}
        heap = []
        if not self.options_by_raw:
            for score, task_id_list_str, courier_id, willingness in self.candidates:
                if _task_count(task_id_list_str) != 1:
                    continue
                cost = _expected_cost(score, task_id_list_str, willingness)
                old = self.options_by_raw.setdefault(task_id_list_str, {}).get(courier_id)
                if old is None or cost < old:
                    self.options_by_raw[task_id_list_str][courier_id] = cost

        def push_options_for_row(row_index):
            raw, courier_list = rows[row_index]
            old_cost = self.row_cost(raw, courier_list)
            for courier_id in self.options_by_raw.get(raw, {}):
                if courier_id in used_couriers:
                    continue
                new_list = courier_list + [courier_id]
                new_cost = self.row_cost(raw, new_list)
                delta = new_cost - old_cost
                if delta < -1e-09:
                    heapq.heappush(heap, (delta, raw, courier_id, row_index, old_cost))
        for idx in range(len(rows)):
            push_options_for_row(idx)
        while heap and self.time_left() > 0.08:
            delta, raw, courier_id, row_index, old_cost = heapq.heappop(heap)
            if courier_id in used_couriers:
                continue
            if row_index >= len(rows) or rows[row_index][0] != raw:
                row_index = raw_to_index.get(raw, -1)
                if row_index < 0:
                    continue
            current_cost = self.row_cost(raw, rows[row_index][1])
            if abs(current_cost - old_cost) > 1e-09:
                new_cost = self.row_cost(raw, rows[row_index][1] + [courier_id])
                new_delta = new_cost - current_cost
                if new_delta < -1e-09:
                    heapq.heappush(heap, (new_delta, raw, courier_id, row_index, current_cost))
                continue
            rows[row_index][1].append(courier_id)
            rows[row_index][1].sort(key=lambda c: (self.info_map[raw, c][0], c))
            used_couriers.add(courier_id)
            if len(used_couriers) >= len(self.all_couriers):
                break
            push_options_for_row(row_index)
        return [(raw, courier_list) for raw, courier_list in rows]

    def strategy_multi_single_greedy(self):
        return self._multi_from_base(self.strategy_exact_single_matching())

    def _first_extra_matching_from_base(self, base):
        if not base:
            return None
        rows = [[raw, list(courier_list)] for raw, courier_list in base]
        used_couriers = {courier_id for _, courier_list in rows for courier_id in courier_list}
        free_couriers = [c for c in self.all_couriers if c not in used_couriers]
        if not free_couriers:
            return [(raw, courier_list) for raw, courier_list in rows]
        n_free = len(free_couriers)
        n_rows = len(rows)
        source = 0
        courier_base = 1
        row_base = courier_base + n_free
        sink = row_base + n_rows
        graph = [[] for _ in range(sink + 1)]

        def add_edge(u, v, cap, cost, payload=None):
            graph[u].append([v, cap, cost, len(graph[v]), payload])
            graph[v].append([u, 0, -cost, len(graph[u]) - 1, None])
        for i in range(n_free):
            add_edge(source, courier_base + i, 1, 0.0)
        row_base_costs = [self.row_cost(raw, courier_list) for raw, courier_list in rows]
        edge_count = 0
        for ci, courier_id in enumerate(free_couriers):
            courier_node = courier_base + ci
            for ri, (raw, courier_list) in enumerate(rows):
                if (raw, courier_id) not in self.info_map:
                    continue
                delta = self.row_cost(raw, courier_list + [courier_id]) - row_base_costs[ri]
                if delta < -1e-09:
                    add_edge(courier_node, row_base + ri, 1, delta, (ci, ri))
                    edge_count += 1
        if edge_count == 0:
            return [(raw, courier_list) for raw, courier_list in rows]
        for ri in range(n_rows):
            add_edge(row_base + ri, sink, 1, 0.0)
        while self.time_left() > 0.2:
            dist = [10 ** 30] * len(graph)
            prev = [None] * len(graph)
            in_queue = [False] * len(graph)
            queue = [source]
            dist[source] = 0.0
            in_queue[source] = True
            head = 0
            while head < len(queue):
                u = queue[head]
                head += 1
                in_queue[u] = False
                for edge_index, edge in enumerate(graph[u]):
                    if edge[1] <= 0:
                        continue
                    v = edge[0]
                    nd = dist[u] + edge[2]
                    if nd < dist[v] - 1e-12:
                        dist[v] = nd
                        prev[v] = (u, edge_index)
                        if not in_queue[v]:
                            queue.append(v)
                            in_queue[v] = True
            if prev[sink] is None or dist[sink] >= -1e-09:
                break
            v = sink
            while v != source:
                u, edge_index = prev[v]
                edge = graph[u][edge_index]
                edge[1] -= 1
                graph[v][edge[3]][1] += 1
                v = u
        for ci, courier_id in enumerate(free_couriers):
            node = courier_base + ci
            for edge in graph[node]:
                payload = edge[4]
                if payload is not None and edge[1] == 0:
                    _, row_index = payload
                    rows[row_index][1].append(courier_id)
                    break
        for raw, courier_list in rows:
            courier_list.sort(key=lambda c: (self.info_map.get((raw, c), (10 ** 30, 0.0, 10 ** 30))[0], c))
        return [(raw, courier_list) for raw, courier_list in rows]

    def strategy_two_stage_extra_matching(self):
        if self.scarce_mode:
            return None
        best = None
        best_m = None
        if len(self.all_tasks) >= 40:
            penalties = (45.0, 60.0, 80.0, 100.0, 130.0, 180.0, 260.0)
        else:
            penalties = (80.0, 100.0, 60.0, 110.0, 130.0, 160.0, 200.0)
        for penalty in penalties:
            if self.time_left() <= 0.45:
                break
            base = _min_cost_single_assignment(self.candidates, penalty)
            if not base:
                continue
            result = self._first_extra_matching_from_base(base)
            result = self._multi_from_base(result)
            m = self.evaluate(result)
            if self.is_better(m, best_m):
                best = result
                best_m = m
        return best

    def strategy_multi_seed_portfolio(self):
        if self.scarce_mode:
            return None
        best = None
        best_m = None
        for penalty in (60.0, 110.0, 200.0):
            if self.time_left() <= 0.25:
                break
            base = _min_cost_single_assignment(self.candidates, penalty)
            if not base:
                continue
            result = self._multi_from_base(base)
            m = self.evaluate(result)
            if self.is_better(m, best_m):
                best = result
                best_m = m
        return best

    def strategy_low_pair_bundle_portfolio(self):
        if self.scarce_mode or self.max_willingness >= 0.42 or (not self.pair_raw_by_tasks):
            return None
        raw_orders = [sorted(self.raw_tasks, key=lambda raw: (self.best_raw_score.get(raw, 10 ** 30) / max(1, len(self.raw_tasks.get(raw, ()))), self.best_raw_score.get(raw, 10 ** 30), -len(self.raw_tasks.get(raw, ())), raw)), sorted(self.pair_raws, key=lambda raw: (self.best_raw_score.get(raw, 10 ** 30), raw)) + [self.single_raw_by_task[t] for t in self.all_tasks if t in self.single_raw_by_task]]
        best = None
        best_m = None
        for raw_order in raw_orders:
            if self.time_left() <= 0.45:
                break
            partition = self._partition_from_order(raw_order)
            if not partition:
                continue
            result = self.assign_partition(partition)
            result = self._multi_from_base(result)
            rows = [[raw, list(cl)] for raw, cl in result]
            self._quick_local_search(rows)
            result = [(raw, cl) for raw, cl in rows]
            m = self.evaluate(result)
            if self.is_better(m, best_m):
                best = result
                best_m = m
        return best

    def _solution_probability_stats(self, result):
        if not result:
            return ({}, 0.0, 0.0)
        length_counts = {}
        p_total = 0.0
        expected_total = 0.0
        count = 0
        for raw, couriers in result:
            length_counts[len(couriers)] = length_counts.get(len(couriers), 0) + 1
            fail_prob = 1.0
            weighted_score = 0.0
            willingness_sum = 0.0
            for courier_id in couriers:
                info = self.info_map.get((raw, courier_id))
                if info is None:
                    continue
                score, willingness, _ = info
                weighted_score += willingness * score
                willingness_sum += willingness
                fail_prob *= 1.0 - willingness
            if willingness_sum > 1e-12:
                p_total += 1.0 - fail_prob
                expected_total += weighted_score / willingness_sum
                count += 1
        if count == 0:
            return (length_counts, 0.0, 0.0)
        return (length_counts, p_total / count, expected_total / count)

    def strategy_multi_local_search(self):
        if self.scarce_mode:
            return None
        base = self.best_result if self.best_result else self.strategy_multi_single_greedy()
        if not base:
            return None
        rows = [[raw, list(courier_list)] for raw, courier_list in base]
        row_costs = [self.row_cost(raw, courier_list) for raw, courier_list in rows]
        n_rows = len(rows)
        for _ in range(120):
            if self.time_left() <= 0.1:
                break
            best = (0.0, None)
            for i, (raw_i, couriers_i) in enumerate(rows):
                if len(couriers_i) <= 1:
                    continue
                for courier_id in tuple(couriers_i):
                    new_i_list = [c for c in couriers_i if c != courier_id]
                    new_i_cost = self.row_cost(raw_i, new_i_list)
                    for j, (raw_j, couriers_j) in enumerate(rows):
                        if i == j or (raw_j, courier_id) not in self.info_map:
                            continue
                        new_j_list = couriers_j + [courier_id]
                        delta = new_i_cost + self.row_cost(raw_j, new_j_list) - row_costs[i] - row_costs[j]
                        if delta < best[0] - 1e-09:
                            best = (delta, ('move', i, j, courier_id, new_i_list, new_j_list))
            for i in range(n_rows):
                raw_i, couriers_i = rows[i]
                for j in range(i + 1, n_rows):
                    raw_j, couriers_j = rows[j]
                    for courier_i in tuple(couriers_i):
                        if (raw_j, courier_i) not in self.info_map:
                            continue
                        for courier_j in tuple(couriers_j):
                            if (raw_i, courier_j) not in self.info_map:
                                continue
                            if courier_i == courier_j:
                                continue
                            new_i_list = [courier_j if c == courier_i else c for c in couriers_i]
                            new_j_list = [courier_i if c == courier_j else c for c in couriers_j]
                            delta = self.row_cost(raw_i, new_i_list) + self.row_cost(raw_j, new_j_list) - row_costs[i] - row_costs[j]
                            if delta < best[0] - 1e-09:
                                best = (delta, ('swap', i, j, new_i_list, new_j_list))
            if best[1] is None:
                break
            action = best[1]
            if action[0] == 'move':
                _, i, j, _, new_i_list, new_j_list = action
                rows[i][1] = new_i_list
                rows[j][1] = new_j_list
                row_costs[i] = self.row_cost(rows[i][0], rows[i][1])
                row_costs[j] = self.row_cost(rows[j][0], rows[j][1])
            else:
                _, i, j, new_i_list, new_j_list = action
                rows[i][1] = new_i_list
                rows[j][1] = new_j_list
                row_costs[i] = self.row_cost(rows[i][0], rows[i][1])
                row_costs[j] = self.row_cost(rows[j][0], rows[j][1])
        for _ in range(6):
            if self.time_left() <= 0.2:
                break
            best = (0.0, None)
            stop_scan = False
            for i in range(n_rows):
                raw_i, couriers_i = rows[i]
                for j in range(i + 1, n_rows):
                    raw_j, couriers_j = rows[j]
                    for k in range(j + 1, n_rows):
                        if self.time_left() <= 0.2:
                            stop_scan = True
                            break
                        raw_k, couriers_k = rows[k]
                        base_cost = row_costs[i] + row_costs[j] + row_costs[k]
                        for courier_i in tuple(couriers_i):
                            for courier_j in tuple(couriers_j):
                                for courier_k in tuple(couriers_k):
                                    if (raw_j, courier_i) in self.info_map and (raw_k, courier_j) in self.info_map and ((raw_i, courier_k) in self.info_map):
                                        new_i = [courier_k if c == courier_i else c for c in couriers_i]
                                        new_j = [courier_i if c == courier_j else c for c in couriers_j]
                                        new_k = [courier_j if c == courier_k else c for c in couriers_k]
                                        delta = self.row_cost(raw_i, new_i) + self.row_cost(raw_j, new_j) + self.row_cost(raw_k, new_k) - base_cost
                                        if delta < best[0] - 1e-09:
                                            best = (delta, (i, j, k, new_i, new_j, new_k))
                                    if (raw_i, courier_j) in self.info_map and (raw_j, courier_k) in self.info_map and ((raw_k, courier_i) in self.info_map):
                                        new_i = [courier_j if c == courier_i else c for c in couriers_i]
                                        new_j = [courier_k if c == courier_j else c for c in couriers_j]
                                        new_k = [courier_i if c == courier_k else c for c in couriers_k]
                                        delta = self.row_cost(raw_i, new_i) + self.row_cost(raw_j, new_j) + self.row_cost(raw_k, new_k) - base_cost
                                        if delta < best[0] - 1e-09:
                                            best = (delta, (i, j, k, new_i, new_j, new_k))
                    if stop_scan:
                        break
                if stop_scan:
                    break
            if best[1] is None:
                break
            i, j, k, new_i, new_j, new_k = best[1]
            rows[i][1] = new_i
            rows[j][1] = new_j
            rows[k][1] = new_k
            row_costs[i] = self.row_cost(rows[i][0], rows[i][1])
            row_costs[j] = self.row_cost(rows[j][0], rows[j][1])
            row_costs[k] = self.row_cost(rows[k][0], rows[k][1])
        if n_rows <= 30:
            for _ in range(3):
                if self.time_left() <= 0.3:
                    break
                best = (0.0, None)
                stop_scan = False
                for i in range(n_rows):
                    raw_i, couriers_i = rows[i]
                    for j in range(i + 1, n_rows):
                        raw_j, couriers_j = rows[j]
                        for k in range(j + 1, n_rows):
                            raw_k, couriers_k = rows[k]
                            for l in range(k + 1, n_rows):
                                if self.time_left() <= 0.3:
                                    stop_scan = True
                                    break
                                raw_l, couriers_l = rows[l]
                                base_cost = row_costs[i] + row_costs[j] + row_costs[k] + row_costs[l]
                                for courier_i in tuple(couriers_i):
                                    for courier_j in tuple(couriers_j):
                                        for courier_k in tuple(couriers_k):
                                            for courier_l in tuple(couriers_l):
                                                if (raw_j, courier_i) in self.info_map and (raw_k, courier_j) in self.info_map and ((raw_l, courier_k) in self.info_map) and ((raw_i, courier_l) in self.info_map):
                                                    new_i = [courier_l if c == courier_i else c for c in couriers_i]
                                                    new_j = [courier_i if c == courier_j else c for c in couriers_j]
                                                    new_k = [courier_j if c == courier_k else c for c in couriers_k]
                                                    new_l = [courier_k if c == courier_l else c for c in couriers_l]
                                                    delta = self.row_cost(raw_i, new_i) + self.row_cost(raw_j, new_j) + self.row_cost(raw_k, new_k) + self.row_cost(raw_l, new_l) - base_cost
                                                    if delta < best[0] - 1e-09:
                                                        best = (delta, (i, j, k, l, new_i, new_j, new_k, new_l))
                                                if (raw_l, courier_i) in self.info_map and (raw_k, courier_l) in self.info_map and ((raw_j, courier_k) in self.info_map) and ((raw_i, courier_j) in self.info_map):
                                                    new_i = [courier_j if c == courier_i else c for c in couriers_i]
                                                    new_j = [courier_k if c == courier_j else c for c in couriers_j]
                                                    new_k = [courier_l if c == courier_k else c for c in couriers_k]
                                                    new_l = [courier_i if c == courier_l else c for c in couriers_l]
                                                    delta = self.row_cost(raw_i, new_i) + self.row_cost(raw_j, new_j) + self.row_cost(raw_k, new_k) + self.row_cost(raw_l, new_l) - base_cost
                                                    if delta < best[0] - 1e-09:
                                                        best = (delta, (i, j, k, l, new_i, new_j, new_k, new_l))
                            if stop_scan:
                                break
                        if stop_scan:
                            break
                    if stop_scan:
                        break
                if best[1] is None:
                    break
                i, j, k, l, new_i, new_j, new_k, new_l = best[1]
                rows[i][1] = new_i
                rows[j][1] = new_j
                rows[k][1] = new_k
                rows[l][1] = new_l
                row_costs[i] = self.row_cost(rows[i][0], rows[i][1])
                row_costs[j] = self.row_cost(rows[j][0], rows[j][1])
                row_costs[k] = self.row_cost(rows[k][0], rows[k][1])
                row_costs[l] = self.row_cost(rows[l][0], rows[l][1])
        length_counts, p_avg, _ = self._solution_probability_stats([(raw, courier_list) for raw, courier_list in rows])
        if n_rows <= 30 and p_avg < 0.8:
            self._low_willingness_lns(rows, row_costs)
        return [(raw, courier_list) for raw, courier_list in rows]

    def _low_willingness_lns(self, rows, row_costs):
        deep = EXPLORE_MODE == 'low_lns5'
        for _round in range(8):
            if self.time_left() <= 0.3:
                break
            high_rows = sorted(range(len(rows)), key=lambda i: row_costs[i], reverse=True)[:12]
            imbalanced = sorted((i for i, (_, courier_list) in enumerate(rows) if len(courier_list) != 2), key=lambda i: (len(rows[i][1]), -row_costs[i], rows[i][0]))
            candidate_rows = list(dict.fromkeys(high_rows + imbalanced))[:18 if deep else 16]
            best = (0.0, None)
            checked = 0
            for size in (4, 5) if deep else (4,):
                if len(candidate_rows) < size:
                    continue
                for indexes in itertools.combinations(candidate_rows, size):
                    if self.time_left() <= 0.3 or checked >= (700 if deep else 400):
                        break
                    checked += 1
                    raws = [rows[i][0] for i in indexes]
                    couriers = []
                    for i in indexes:
                        couriers.extend(rows[i][1])
                    if len(couriers) > (14 if deep else 12):
                        continue
                    base_cost = sum((row_costs[i] for i in indexes))
                    feasible = []
                    for courier_id in couriers:
                        choices = [pos for pos, raw in enumerate(raws) if (raw, courier_id) in self.info_map]
                        if not choices:
                            feasible = []
                            break
                        feasible.append((len(choices), courier_id, choices))
                    if not feasible:
                        continue
                    feasible.sort(key=lambda x: (x[0], x[1]))
                    assignment = [[] for _ in raws]
                    best_local = [base_cost, None]
                    nodes = [0]

                    def rec(pos):
                        if nodes[0] > (50000 if deep else 30000) or self.time_left() <= 0.3:
                            return
                        nodes[0] += 1
                        if pos == len(feasible):
                            if any((not part for part in assignment)):
                                return
                            total = 0.0
                            for idx, raw in enumerate(raws):
                                total += self.row_cost(raw, assignment[idx])
                                if total >= best_local[0] - 1e-12:
                                    return
                            if total < best_local[0] - 1e-09:
                                best_local[0] = total
                                best_local[1] = [list(part) for part in assignment]
                            return
                        remaining = len(feasible) - pos
                        empty = sum((1 for part in assignment if not part))
                        if remaining < empty:
                            return
                        _, courier_id, choices = feasible[pos]
                        ordered_choices = sorted(choices, key=lambda idx: row_costs[indexes[idx]], reverse=True)
                        for idx in ordered_choices:
                            assignment[idx].append(courier_id)
                            rec(pos + 1)
                            assignment[idx].pop()
                    rec(0)
                    if best_local[1] is not None:
                        delta = best_local[0] - base_cost
                        if delta < best[0] - 1e-09:
                            best = (delta, (indexes, best_local[1]))
                if self.time_left() <= 0.3 or checked >= (700 if deep else 400):
                    break
            if best[1] is None:
                break
            indexes, new_assignment = best[1]
            for row_index, courier_list in zip(indexes, new_assignment):
                rows[row_index][1] = courier_list
                row_costs[row_index] = self.row_cost(rows[row_index][0], courier_list)

    def assign_partition(self, partition):
        partition = list(dict.fromkeys(partition))
        if not partition:
            return None
        cache_key = tuple(sorted(partition))
        if cache_key in self.assignment_cache:
            return list(self.assignment_cache[cache_key])
        couriers = self.all_couriers
        courier_idx = {courier_id: i for i, courier_id in enumerate(couriers)}
        n_rows = len(partition)
        n_couriers = len(couriers)
        source = 0
        row_base = 1
        courier_base = row_base + n_rows
        sink = courier_base + n_couriers
        graph = [[] for _ in range(sink + 1)]

        def add_edge(u, v, cap, cost, payload=None):
            graph[u].append([v, cap, cost, len(graph[v]), payload])
            graph[v].append([u, 0, -cost, len(graph[u]) - 1, None])
        for i, raw in enumerate(partition):
            add_edge(source, row_base + i, 1, 0)
            for courier_id, score in self.options_by_raw.get(raw, {}).items():
                add_edge(row_base + i, courier_base + courier_idx[courier_id], 1, score, (raw, courier_id))
        for courier_id in couriers:
            add_edge(courier_base + courier_idx[courier_id], sink, 1, 0)
        flow = 0
        potentials = [0.0] * len(graph)
        target_flow = min(n_rows, n_couriers)
        while flow < target_flow:
            dist = [10 ** 30] * len(graph)
            prev = [None] * len(graph)
            dist[source] = 0.0
            heap = [(0.0, source)]
            while heap:
                d, u = heapq.heappop(heap)
                if d > dist[u] + 1e-12:
                    continue
                for edge_index, edge in enumerate(graph[u]):
                    if edge[1] <= 0:
                        continue
                    v = edge[0]
                    nd = d + edge[2] + potentials[u] - potentials[v]
                    if nd < dist[v] - 1e-12:
                        dist[v] = nd
                        prev[v] = (u, edge_index)
                        heapq.heappush(heap, (nd, v))
            if prev[sink] is None:
                break
            for i, d in enumerate(dist):
                if d < 10 ** 29:
                    potentials[i] += d
            v = sink
            while v != source:
                u, edge_index = prev[v]
                edge = graph[u][edge_index]
                edge[1] -= 1
                graph[v][edge[3]][1] += 1
                v = u
            flow += 1
        result = []
        for i, raw in enumerate(partition):
            node = row_base + i
            for edge in graph[node]:
                payload = edge[4]
                if payload is not None and edge[1] == 0:
                    result.append((payload[0], [payload[1]]))
                    break
        self.assignment_cache[cache_key] = tuple(result)
        return result

    def _partition_from_order(self, raw_order):
        used_tasks = set()
        partition = []
        max_rows = len(self.all_couriers)
        for raw in raw_order:
            tasks = self.raw_tasks.get(raw, ())
            if not tasks or any((task_id in used_tasks for task_id in tasks)):
                continue
            partition.append(raw)
            used_tasks.update(tasks)
            if len(used_tasks) == len(self.all_tasks) or len(partition) >= max_rows:
                break
        return partition

    def strategy_pair_density_matching(self):
        raw_order = sorted(self.raw_tasks, key=lambda raw: (self.best_raw_score.get(raw, 10 ** 30) / max(1, len(self.raw_tasks.get(raw, ()))), self.best_raw_score.get(raw, 10 ** 30), -len(self.raw_tasks.get(raw, ())), raw))
        return self.assign_partition(self._partition_from_order(raw_order))

    def strategy_pair_saving_matching(self):

        def saving_key(raw):
            tasks = self.raw_tasks.get(raw, ())
            if len(tasks) != 2:
                return (10 ** 30, self.best_raw_score.get(raw, 10 ** 30), raw)
            single_sum = 0.0
            for task_id in tasks:
                single_raw = self.single_raw_by_task.get(task_id)
                if single_raw is None:
                    return (10 ** 30, self.best_raw_score.get(raw, 10 ** 30), raw)
                single_sum += self.best_raw_score.get(single_raw, 10 ** 30)
            saving = single_sum - self.best_raw_score.get(raw, 10 ** 30)
            return (-saving, self.best_raw_score.get(raw, 10 ** 30), raw)
        pair_order = sorted(self.pair_raws, key=saving_key)
        singles = [self.single_raw_by_task[t] for t in self.all_tasks if t in self.single_raw_by_task]
        return self.assign_partition(self._partition_from_order(pair_order + singles))

    def strategy_scarce_alt_partition(self):
        if not self.best_result:
            return None
        used = {raw for raw, _ in self.best_result}
        alt = [raw for raw in self.pair_raws if raw not in used]
        tails = sorted(used, key=lambda raw: (self.best_raw_score.get(raw, 10 ** 30), raw))
        orders = [sorted(alt, key=lambda raw: (self.best_raw_score.get(raw, 10 ** 30), raw)), sorted(alt, key=lambda raw: (self.best_raw_score.get(raw, 10 ** 30) / max(1, len(self.raw_tasks.get(raw, ()))), raw))]
        best = None
        best_m = None
        for order in orders:
            result = self.assign_partition(self._partition_from_order(order + tails))
            metrics = self.evaluate(result)
            if metrics['valid'] and metrics['accepted_count'] == len(self.all_tasks):
                changed = sum((1 for raw, _ in result if raw not in used))
                score = dict(metrics, total_score=metrics['total_score'] - 0.001 * changed)
                if self.is_better(score, best_m):
                    best = result
                    best_m = score
        return best

    def _scarce_seed_partitions(self):
        raw_orders = [sorted(self.raw_tasks, key=lambda raw: (self.best_raw_score.get(raw, 10 ** 30) / max(1, len(self.raw_tasks.get(raw, ()))), self.best_raw_score.get(raw, 10 ** 30), -len(self.raw_tasks.get(raw, ())), raw)), sorted(self.raw_tasks, key=lambda raw: (-len(self.raw_tasks.get(raw, ())), self.best_raw_score.get(raw, 10 ** 30), raw))]
        seeds = []
        for raw_order in raw_orders:
            partition = self._partition_from_order(raw_order)
            if partition:
                seeds.append(partition)
        saving_result = self.strategy_pair_saving_matching()
        if saving_result:
            seeds.append([raw for raw, _ in saving_result])
        unique = []
        seen = set()
        for partition in seeds:
            key = tuple(sorted(partition))
            if key not in seen:
                seen.add(key)
                unique.append(partition)
        return unique

    def strategy_pair_local_refine(self):
        seeds = self._scarce_seed_partitions()
        if not seeds:
            return None
        best_partition = None
        best_metrics = None
        for partition in seeds:
            result = self.assign_partition(partition)
            metrics = self.evaluate(result)
            if self.is_better(metrics, best_metrics):
                best_partition = partition
                best_metrics = metrics
        if not best_partition:
            return None
        current = list(best_partition)
        current_metrics = best_metrics
        for _round in range(5):
            if self.time_left() <= 0.2:
                break
            pair_rows = [raw for raw in current if len(self.raw_tasks.get(raw, ())) == 2]
            if len(pair_rows) < 2:
                break
            next_partition = None
            next_metrics = current_metrics
            swap_candidates = []
            for i in range(len(pair_rows)):
                a, b = self.raw_tasks[pair_rows[i]]
                for j in range(i + 1, len(pair_rows)):
                    c, d = self.raw_tasks[pair_rows[j]]
                    alternatives = [(tuple(sorted((a, c))), tuple(sorted((b, d)))), (tuple(sorted((a, d))), tuple(sorted((b, c))))]
                    for p1, p2 in alternatives:
                        raw1 = self.pair_raw_by_tasks.get(p1)
                        raw2 = self.pair_raw_by_tasks.get(p2)
                        if raw1 is None or raw2 is None or raw1 == raw2:
                            continue
                        approx_delta = self.best_raw_score.get(raw1, 10 ** 30) + self.best_raw_score.get(raw2, 10 ** 30) - self.best_raw_score.get(pair_rows[i], 10 ** 30) - self.best_raw_score.get(pair_rows[j], 10 ** 30)
                        if approx_delta > 3.0:
                            continue
                        swap_candidates.append((approx_delta, pair_rows[i], pair_rows[j], raw1, raw2))
            swap_candidates.sort(key=lambda x: x[0])
            exact_limit = 90 if len(pair_rows) <= 22 else 45
            for _, old1, old2, raw1, raw2 in swap_candidates[:exact_limit]:
                if self.time_left() <= 0.2:
                    break
                candidate_partition = [raw for raw in current if raw not in (old1, old2)] + [raw1, raw2]
                if len(set(candidate_partition)) != len(candidate_partition):
                    continue
                result = self.assign_partition(candidate_partition)
                metrics = self.evaluate(result)
                if self.is_better(metrics, next_metrics):
                    next_partition = candidate_partition
                    next_metrics = metrics
            if next_partition is None:
                break
            current = next_partition
            current_metrics = next_metrics
        return self.assign_partition(current)

    def _enumerate_pair_covers(self, task_ids, limit=120):
        task_ids = tuple(sorted(task_ids))
        results = []

        def rec(remaining, partition):
            if len(results) >= limit:
                return
            if not remaining:
                results.append(tuple(partition))
                return
            first = remaining[0]
            single_raw = self.single_raw_by_task.get(first)
            if single_raw is not None:
                rec(remaining[1:], partition + [single_raw])
            pair_choices = []
            for idx in range(1, len(remaining)):
                other = remaining[idx]
                raw = self.pair_raw_by_tasks.get(tuple(sorted((first, other))))
                if raw is not None:
                    pair_choices.append((self.best_raw_score.get(raw, 10 ** 30), idx, raw))
            pair_choices.sort(key=lambda x: (x[0], x[2]))
            for _, idx, raw in pair_choices:
                rec(remaining[1:idx] + remaining[idx + 1:], partition + [raw])
        rec(task_ids, [])
        results.sort(key=lambda rows: (sum((self.best_raw_score.get(raw, 10 ** 30) for raw in rows)), len(rows), rows))
        return results[:limit]

    def strategy_scarce_subset_repair(self):
        if not self.scarce_mode or not self.best_result or (not self.pair_raw_by_tasks):
            return None
        current = [raw for raw, _ in self.best_result]
        current_metrics = self.evaluate(self.assign_partition(current))
        if not current_metrics['valid']:
            return None
        max_rows = len(self.all_couriers)
        deep = False
        safe_time = 0.28 if deep else 0.2
        for _round in range(7 if deep else 4):
            if self.time_left() <= safe_time:
                break
            rows = list(current)
            combos = []
            for size in (2, 3, 4) if deep else (2, 3):
                for indexes in itertools.combinations(range(len(rows)), size):
                    task_set = set()
                    for idx in indexes:
                        task_set.update(self.raw_tasks.get(rows[idx], ()))
                    if 2 <= len(task_set) <= (9 if deep else 7):
                        old_approx = sum((self.best_raw_score.get(rows[idx], 10 ** 30) for idx in indexes))
                        combos.append((len(task_set), old_approx, indexes, task_set))
            combos.sort(key=lambda x: (x[0], -x[1], x[2]))
            improved = False
            for _, old_approx, indexes, task_set in combos[:6200 if deep else 2600]:
                if self.time_left() <= safe_time:
                    break
                old_rows = {rows[idx] for idx in indexes}
                base = [raw for raw in current if raw not in old_rows]
                base_set = set(base)
                covers = self._enumerate_pair_covers(task_set, 180 if deep else 70)
                for cover in covers:
                    if self.time_left() <= safe_time:
                        break
                    if set(cover) == old_rows:
                        continue
                    if len(base) + len(cover) > max_rows:
                        continue
                    if any((raw in base_set for raw in cover)):
                        continue
                    new_approx = sum((self.best_raw_score.get(raw, 10 ** 30) for raw in cover))
                    if new_approx > old_approx + (18.0 if deep else 5.0):
                        continue
                    candidate_partition = base + list(cover)
                    if len(candidate_partition) != len(set(candidate_partition)):
                        continue
                    result = self.assign_partition(candidate_partition)
                    metrics = self.evaluate(result)
                    if self.is_better(metrics, current_metrics):
                        current = candidate_partition
                        current_metrics = metrics
                        improved = True
                        break
                if improved:
                    break
            if not improved:
                break
        return self.assign_partition(current)

    def _solve_fixed_courier_pair_subset(self, task_ids, courier_ids):
        task_ids = tuple(sorted(task_ids))
        courier_ids = tuple(sorted(courier_ids))
        n_tasks = len(task_ids)
        n_couriers = len(courier_ids)
        if n_tasks != 2 * n_couriers or n_couriers <= 0:
            return None
        full_task_mask = (1 << n_tasks) - 1
        full_courier_mask = (1 << n_couriers) - 1
        memo = {}
        choice = {}

        def dp(task_mask, courier_mask):
            key = (task_mask, courier_mask)
            if key in memo:
                return memo[key]
            if task_mask == full_task_mask:
                return 0.0 if courier_mask == full_courier_mask else 10 ** 30
            first = 0
            while task_mask & 1 << first:
                first += 1
            best = 10 ** 30
            best_choice = None
            for other in range(first + 1, n_tasks):
                if task_mask & 1 << other:
                    continue
                raw = self.pair_raw_by_tasks.get(tuple(sorted((task_ids[first], task_ids[other]))))
                if raw is None:
                    continue
                next_task_mask = task_mask | 1 << first | 1 << other
                for ci, courier_id in enumerate(courier_ids):
                    if courier_mask & 1 << ci:
                        continue
                    if (raw, courier_id) not in self.info_map:
                        continue
                    tail = dp(next_task_mask, courier_mask | 1 << ci)
                    if tail >= 10 ** 29:
                        continue
                    cost = self.row_cost(raw, [courier_id]) + tail
                    if cost < best - 1e-12:
                        best = cost
                        best_choice = (raw, courier_id, next_task_mask, courier_mask | 1 << ci)
            memo[key] = best
            choice[key] = best_choice
            return best
        best_cost = dp(0, 0)
        if best_cost >= 10 ** 29:
            return None
        result = []
        key = (0, 0)
        while key != (full_task_mask, full_courier_mask):
            item = choice.get(key)
            if item is None:
                return None
            raw, courier_id, next_task_mask, next_courier_mask = item
            result.append((raw, [courier_id]))
            key = (next_task_mask, next_courier_mask)
        return result

    def strategy_scarce_exact_lns(self):
        if not self.scarce_mode or not self.best_result or (not self.pair_raw_by_tasks):
            return None
        current = [(raw, list(courier_list)) for raw, courier_list in self.best_result]
        current_metrics = self.evaluate(current)
        if not current_metrics['valid']:
            return None
        deep = EXPLORE_MODE == 'scarce_exact_deep'
        for _round in range(10 if deep else 6):
            if self.time_left() <= 0.25:
                break
            row_costs = [self.row_cost(raw, courier_list) for raw, courier_list in current]
            focus = sorted(range(len(current)), key=lambda i: row_costs[i], reverse=True)[:18 if deep else 14]
            candidates = []
            for size in (3, 4, 5, 6, 7) if deep else (3, 4, 5, 6):
                if len(focus) < size:
                    continue
                for indexes in itertools.combinations(focus, size):
                    task_ids = []
                    courier_ids = []
                    feasible = True
                    for idx in indexes:
                        raw, courier_list = current[idx]
                        tasks = self.raw_tasks.get(raw, ())
                        if len(tasks) != 2 or len(courier_list) != 1:
                            feasible = False
                            break
                        task_ids.extend(tasks)
                        courier_ids.append(courier_list[0])
                    if not feasible or len(set(task_ids)) != len(task_ids):
                        continue
                    old_cost = sum((row_costs[idx] for idx in indexes))
                    candidates.append((-old_cost, indexes, tuple(task_ids), tuple(courier_ids)))
            candidates.sort(key=lambda x: (x[0], x[1]))
            improved = False
            checked = 0
            for _, indexes, task_ids, courier_ids in candidates[:1800 if deep else 700]:
                if self.time_left() <= 0.25 or checked >= (700 if deep else 260):
                    break
                checked += 1
                replacement = self._solve_fixed_courier_pair_subset(task_ids, courier_ids)
                if not replacement:
                    continue
                old_cost = sum((row_costs[idx] for idx in indexes))
                new_cost = sum((self.row_cost(raw, courier_list) for raw, courier_list in replacement))
                if new_cost >= old_cost - 1e-09:
                    continue
                replace_set = set(indexes)
                candidate = [row for i, row in enumerate(current) if i not in replace_set]
                candidate.extend(replacement)
                metrics = self.evaluate(candidate)
                if self.is_better(metrics, current_metrics):
                    current = candidate
                    current_metrics = metrics
                    improved = True
                    break
            if not improved:
                break
        return current

    def strategy_scarce_random_lns(self):
        if not self.scarce_mode or not self.best_result or (not self.pair_raw_by_tasks):
            return None
        current = [(raw, list(courier_list)) for raw, courier_list in self.best_result]
        current_metrics = self.evaluate(current)
        if not current_metrics['valid']:
            return None
        rng = random.Random(20260520)
        seen = set()
        checked = 0
        while self.time_left() > 0.23 and checked < 320:
            row_costs = [self.row_cost(raw, courier_list) for raw, courier_list in current]
            n_rows = len(current)
            if n_rows < 4:
                break
            order = sorted(range(n_rows), key=lambda i: row_costs[i], reverse=True)
            top = order[:min(10, n_rows)]
            pool = order[:min(18, n_rows)]
            improved = False
            batch = []
            for _ in range(36):
                if self.time_left() <= 0.23:
                    break
                size = (4, 5, 6, 5, 6, 7)[checked % 6]
                if size > len(pool):
                    size = len(pool)
                if size < 3:
                    continue
                chosen = {top[(checked + _) % len(top)]}
                if size >= 5 and len(top) >= 2:
                    chosen.add(top[(checked * 3 + _) % len(top)])
                tries = 0
                while len(chosen) < size and tries < 80:
                    tries += 1
                    if rng.randrange(3):
                        idx = top[rng.randrange(len(top))]
                    else:
                        idx = pool[rng.randrange(len(pool))]
                    chosen.add(idx)
                if len(chosen) != size:
                    continue
                indexes = tuple(sorted(chosen))
                if indexes in seen:
                    continue
                seen.add(indexes)
                batch.append(indexes)
            best = (0.0, None)
            for indexes in batch:
                if self.time_left() <= 0.23 or checked >= 320:
                    break
                checked += 1
                task_ids = []
                courier_ids = []
                feasible = True
                for idx in indexes:
                    raw, courier_list = current[idx]
                    tasks = self.raw_tasks.get(raw, ())
                    if len(tasks) != 2 or len(courier_list) != 1:
                        feasible = False
                        break
                    task_ids.extend(tasks)
                    courier_ids.append(courier_list[0])
                if not feasible or len(set(task_ids)) != len(task_ids):
                    continue
                old_cost = sum((row_costs[idx] for idx in indexes))
                replacement = self._solve_fixed_courier_pair_subset(task_ids, courier_ids)
                if not replacement:
                    continue
                new_cost = sum((self.row_cost(raw, courier_list) for raw, courier_list in replacement))
                delta = new_cost - old_cost
                if delta < best[0] - 1e-09:
                    best = (delta, (indexes, replacement))
            if best[1] is None:
                continue
            indexes, replacement = best[1]
            replace_set = set(indexes)
            candidate = [row for i, row in enumerate(current) if i not in replace_set]
            candidate.extend(replacement)
            metrics = self.evaluate(candidate)
            if self.is_better(metrics, current_metrics):
                current = candidate
                current_metrics = metrics
                improved = True
            if not improved and len(seen) > 160:
                break
        return current

    def strategy_scarce_pair_reshuffle(self):
        if not self.scarce_mode or not self.best_result or (not self.pair_raw_by_tasks):
            return None
        current = [raw for raw, _ in self.best_result]
        current_result = self.assign_partition(current)
        current_metrics = self.evaluate(current_result)
        if not current_metrics['valid']:
            return None
        deep = EXPLORE_MODE == 'scarce_reshuffle_deep'
        for _round in range(4 if deep else 2):
            if self.time_left() <= 0.35:
                break
            assigned = self.assign_partition(current)
            row_cost = {raw: self.row_cost(raw, courier_list) for raw, courier_list in assigned}
            pair_rows = [raw for raw in current if len(self.raw_tasks.get(raw, ())) == 2]
            candidates = []
            for i, old_a in enumerate(pair_rows):
                tasks_a = self.raw_tasks[old_a]
                for j in range(i + 1, len(pair_rows)):
                    old_b = pair_rows[j]
                    tasks_b = self.raw_tasks[old_b]
                    old_cost = row_cost.get(old_a, 0.0) + row_cost.get(old_b, 0.0)
                    alternatives = ((tuple(sorted((tasks_a[0], tasks_b[0]))), tuple(sorted((tasks_a[1], tasks_b[1])))), (tuple(sorted((tasks_a[0], tasks_b[1]))), tuple(sorted((tasks_a[1], tasks_b[0])))))
                    for pair_1, pair_2 in alternatives:
                        raw_1 = self.pair_raw_by_tasks.get(pair_1)
                        raw_2 = self.pair_raw_by_tasks.get(pair_2)
                        if raw_1 is None or raw_2 is None or raw_1 == raw_2:
                            continue
                        approx_delta = self.best_raw_score.get(raw_1, 10 ** 30) + self.best_raw_score.get(raw_2, 10 ** 30) - self.best_raw_score.get(old_a, 10 ** 30) - self.best_raw_score.get(old_b, 10 ** 30)
                        candidates.append((approx_delta, -old_cost, old_a, old_b, raw_1, raw_2))
            candidates.sort()
            best = (0.0, None)
            checked = 0
            for _, _, old_a, old_b, raw_1, raw_2 in candidates[:9000 if deep else 2500]:
                if self.time_left() <= 0.35 or checked >= (1200 if deep else 300):
                    break
                checked += 1
                partition = [raw for raw in current if raw not in (old_a, old_b)] + [raw_1, raw_2]
                if len(partition) != len(set(partition)):
                    continue
                result = self.assign_partition(partition)
                metrics = self.evaluate(result)
                if not self.is_better(metrics, current_metrics):
                    continue
                delta = metrics['total_score'] - current_metrics['total_score']
                if delta < best[0] - 1e-09:
                    best = (delta, (partition, metrics))
            if best[1] is None:
                break
            current, current_metrics = best[1]
        return self.assign_partition(current)

    def strategy_pair_beam_matching(self):
        if not self.scarce_mode or not self.pair_raw_by_tasks:
            return None
        task_index = {task_id: i for i, task_id in enumerate(self.all_tasks)}
        n_tasks = len(self.all_tasks)
        full_mask = (1 << n_tasks) - 1
        max_rows = len(self.all_couriers)
        pair_options = {}
        for raw in self.pair_raws:
            tasks = self.raw_tasks.get(raw, ())
            if len(tasks) != 2:
                continue
            a = task_index.get(tasks[0])
            b = task_index.get(tasks[1])
            if a is None or b is None:
                continue
            pair_options.setdefault(a, []).append((self.best_raw_score.get(raw, 10 ** 30), b, raw))
            pair_options.setdefault(b, []).append((self.best_raw_score.get(raw, 10 ** 30), a, raw))
        for task_id in pair_options:
            pair_options[task_id].sort(key=lambda x: (x[0], x[2]))
        singleton_options = {}
        for task_id, raw in self.single_raw_by_task.items():
            idx = task_index.get(task_id)
            if idx is not None:
                singleton_options[idx] = (self.best_raw_score.get(raw, 10 ** 30), raw)
        beam_width = 900 if n_tasks <= 44 else 260
        branch_limit = 42 if n_tasks <= 44 else 18
        beam = [(0, 0.0, tuple())]
        while beam and self.time_left() > 0.3:
            finished = True
            next_states = []
            for mask, approx_score, partition in beam:
                if mask == full_mask or len(partition) >= max_rows:
                    next_states.append((mask, approx_score, partition))
                    continue
                finished = False
                first = 0
                while first < n_tasks and mask & 1 << first:
                    first += 1
                if first >= n_tasks:
                    next_states.append((mask, approx_score, partition))
                    continue
                added = 0
                for pair_score, other, raw in pair_options.get(first, []):
                    if mask & 1 << other:
                        continue
                    next_states.append((mask | 1 << first | 1 << other, approx_score + pair_score, partition + (raw,)))
                    added += 1
                    if added >= branch_limit:
                        break
                remaining_after_single = n_tasks - _bit_count(mask | 1 << first)
                rows_left_after_single = max_rows - len(partition) - 1
                if rows_left_after_single * 2 >= remaining_after_single and first in singleton_options:
                    single_score, raw = singleton_options[first]
                    next_states.append((mask | 1 << first, approx_score + single_score, partition + (raw,)))
            if finished:
                break
            best_by_mask = {}
            for state in next_states:
                mask, approx_score, partition = state
                old = best_by_mask.get(mask)
                if old is None or approx_score < old[1] - 1e-12:
                    best_by_mask[mask] = state
            beam = sorted(best_by_mask.values(), key=lambda x: (-_bit_count(x[0]), x[1], len(x[2])))[:beam_width]
        candidate_partitions = sorted(beam, key=lambda x: (-_bit_count(x[0]), x[1], len(x[2])))[:24]
        best_result = None
        best_metrics = None
        for _, _, partition in candidate_partitions:
            result = self.assign_partition(partition)
            metrics = self.evaluate(result)
            if self.is_better(metrics, best_metrics):
                best_result = result
                best_metrics = metrics
        return best_result

    def strategy_scarce_dual_pair_cover(self):
        if not self.scarce_mode or not self.pair_raw_by_tasks or self.time_left() <= 0.35:
            return None
        deadline = time.perf_counter() + min(0.75, max(0.12, self.time_left() - 0.25))
        tasks = self.all_tasks
        couriers = self.all_couriers
        ti = {t: i for i, t in enumerate(tasks)}
        ci = {c: i for i, c in enumerate(couriers)}
        n = len(tasks)
        full = (1 << n) - 1
        max_rows = len(couriers)
        seed_cost = {}
        for raw, cs in self.best_result or []:
            if len(cs) == 1:
                seed_cost[cs[0]] = self.row_cost(raw, cs)
        avg = sum(seed_cost.values()) / max(1, len(seed_cost))
        best = None
        best_m = None
        configs = ((0.0, 0, 0.0), (0.16, 1, 0.05), (-0.1, 2, 0.03), (0.26, 3, 0.08))
        for scale, salt, spread_w in configs:
            if time.perf_counter() >= deadline:
                break
            dual = {}
            for k, c in enumerate(couriers):
                jitter = (((k + 3) * 37 + salt * 19) % 29 - 14) * 0.018
                dual[c] = (seed_cost.get(c, avg) - avg) * scale + jitter
            pair_opts = [[] for _ in range(n)]
            for raw in self.pair_raws:
                ts = self.raw_tasks.get(raw, ())
                if len(ts) != 2 or ts[0] not in ti or ts[1] not in ti:
                    continue
                vals = []
                for c, cost in self.options_by_raw.get(raw, {}).items():
                    j = ci.get(c)
                    if j is not None:
                        vals.append((cost + dual.get(c, 0.0), cost, j, c))
                if not vals:
                    continue
                vals.sort(key=lambda x: (x[0], x[3]))
                spread = vals[min(2, len(vals) - 1)][0] - vals[0][0]
                a = ti[ts[0]]
                b = ti[ts[1]]
                for adj, cost, j, c in vals[:5]:
                    key = (adj + spread_w * spread, cost, j, c, raw)
                    pair_opts[a].append((key[0], b, raw, j, c, cost))
                    pair_opts[b].append((key[0], a, raw, j, c, cost))
            for opts in pair_opts:
                opts.sort(key=lambda x: (x[0], x[5], x[2], x[4]))
                del opts[70:]
            singles = {}
            for t, raw in self.single_raw_by_task.items():
                i = ti.get(t)
                if i is None:
                    continue
                vals = []
                for c, cost in self.options_by_raw.get(raw, {}).items():
                    j = ci.get(c)
                    if j is not None:
                        vals.append((cost + dual.get(c, 0.0), raw, j, c, cost))
                if vals:
                    singles[i] = min(vals, key=lambda x: (x[0], x[3]))
            beam = [(0, 0, 0.0, tuple())]
            width = 190 if n <= 44 else 90
            branch = 30 if n <= 44 else 16
            while beam and time.perf_counter() < deadline:
                nxt = []
                done = True
                for mask, cmask, approx, rows in beam:
                    if mask == full:
                        nxt.append((mask, cmask, approx, rows))
                        continue
                    if len(rows) >= max_rows:
                        continue
                    done = False
                    first = 0
                    while first < n and mask & 1 << first:
                        first += 1
                    added = 0
                    for adj, other, raw, cj, c, _ in pair_opts[first]:
                        if mask & 1 << other or cmask & 1 << cj:
                            continue
                        nm = mask | 1 << first | 1 << other
                        if (max_rows - len(rows) - 1) * 2 < n - _bit_count(nm):
                            continue
                        nxt.append((nm, cmask | 1 << cj, approx + adj, rows + ((raw, c),)))
                        added += 1
                        if added >= branch:
                            break
                    if first in singles:
                        adj, raw, cj, c, _ = singles[first]
                        nm = mask | 1 << first
                        if not cmask & 1 << cj and (max_rows - len(rows) - 1) * 2 >= n - _bit_count(nm):
                            nxt.append((nm, cmask | 1 << cj, approx + adj, rows + ((raw, c),)))
                if done or not nxt:
                    break
                keep = {}
                for st in nxt:
                    key = (st[0], st[1])
                    old = keep.get(key)
                    if old is None or st[2] < old[2] - 1e-12:
                        keep[key] = st
                beam = sorted(keep.values(), key=lambda x: (-_bit_count(x[0]), x[2], len(x[3])))[:width]
            for mask, _, _, rows in sorted(beam, key=lambda x: (-_bit_count(x[0]), x[2]))[:18]:
                if mask != full:
                    continue
                result = [(raw, [c]) for raw, c in rows]
                m = self.evaluate(result)
                if self.is_better(m, best_m):
                    best = result
                    best_m = m
        return best

    def strategy_iterated_local_search(self):
        if self.scarce_mode or not self.best_result:
            return None
        best = self.best_result
        best_m = self.best_metrics
        for iteration in range(3):
            if self.time_left() <= 0.6:
                break
            rows = [[raw, list(courier_list)] for raw, courier_list in best]
            n = len(rows)
            perturb_count = min(15, max(6, n // 4))
            row_costs = [(self.row_cost(raw, cl), i, raw, cl) for i, (raw, cl) in enumerate(rows)]
            row_costs.sort(key=lambda x: x[0], reverse=True)
            freed = []
            for _, idx, raw, cl in row_costs[:perturb_count]:
                if len(cl) > 1:
                    worst_c = max(cl, key=lambda c: self.info_map.get((raw, c), (0, 0, 10 ** 30))[2])
                    rows[idx][1] = [c for c in cl if c != worst_c]
                    freed.append(worst_c)
            if not freed:
                break
            for courier_id in freed:
                best_delta = (0.0, None)
                for i, (raw, couriers) in enumerate(rows):
                    if (raw, courier_id) not in self.info_map:
                        continue
                    old_cost = self.row_cost(raw, couriers)
                    new_cost = self.row_cost(raw, couriers + [courier_id])
                    delta = new_cost - old_cost
                    if delta < best_delta[0] - 1e-09:
                        best_delta = (delta, i)
                if best_delta[1] is not None:
                    rows[best_delta[1]][1].append(courier_id)
            self._quick_local_search(rows)
            result = [(raw, cl) for raw, cl in rows]
            m = self.evaluate(result)
            if self.is_better(m, best_m):
                best = result
                best_m = m
        return best if best != self.best_result else None

    def _quick_local_search(self, rows):
        row_costs = [self.row_cost(raw, cl) for raw, cl in rows]
        n = len(rows)
        for _ in range(40):
            if self.time_left() <= 0.05:
                break
            best = (0.0, None)
            for i, (raw_i, couriers_i) in enumerate(rows):
                if len(couriers_i) <= 1:
                    continue
                for courier_id in tuple(couriers_i):
                    new_i_list = [c for c in couriers_i if c != courier_id]
                    new_i_cost = self.row_cost(raw_i, new_i_list)
                    for j, (raw_j, couriers_j) in enumerate(rows):
                        if i == j or (raw_j, courier_id) not in self.info_map:
                            continue
                        new_j_list = couriers_j + [courier_id]
                        delta = new_i_cost + self.row_cost(raw_j, new_j_list) - row_costs[i] - row_costs[j]
                        if delta < best[0] - 1e-09:
                            best = (delta, ('move', i, j, new_i_list, new_j_list))
            if best[1] is None:
                break
            _, i, j, new_i, new_j = best[1]
            rows[i][1] = new_i
            rows[j][1] = new_j
            row_costs[i] = self.row_cost(rows[i][0], rows[i][1])
            row_costs[j] = self.row_cost(rows[j][0], rows[j][1])

    def strategy_optional_milp_backend(self):
        return None

    def run(self):
        n_tasks = len(self.all_tasks)
        n_couriers = len(self.all_couriers)
        ratio = n_couriers / max(1, n_tasks)
        budget = self.time_limit
        self.try_strategy('greedy_min_score', self.strategy_score_greedy)
        self.try_strategy('singleton_first_greedy', self.strategy_singleton_first_greedy)
        self.try_strategy('exact_single_matching', self.strategy_exact_single_matching)
        if not EXPLORE_MODE.startswith('no_history'):
            self.try_strategy('history_feedback_seeds', self.strategy_history_feedback_seeds)
        if self.learned_fast_return():
            return self.best_result
        if not self.scarce_mode:
            self.try_strategy('multi_single_greedy', self.strategy_multi_single_greedy)
            if self.time_left() > 5.8 and self.max_willingness >= 0.42:
                self.try_strategy('two_stage_extra_matching', self.strategy_two_stage_extra_matching)
            if self.time_left() > 5.5 and self.max_willingness >= 0.42:
                self.try_strategy('multi_seed_portfolio', self.strategy_multi_seed_portfolio)
            self.try_strategy('multi_local_search', self.strategy_multi_local_search)
            self.try_strategy('low_pair_bundle_portfolio', self.strategy_low_pair_bundle_portfolio)
            self.try_strategy('optional_milp_backend', self.strategy_optional_milp_backend)
            if self.time_left() > 4.0 and (self.low_willingness_fraction > 0.3 or self.avg_willingness < 0.45):
                self.try_strategy('iterated_local_search', self.strategy_iterated_local_search)
            if self.best_metrics and self.best_metrics['accepted_count'] < min(n_tasks, n_couriers):
                self.try_strategy('density_bundle_greedy', self.strategy_density_greedy)
            if self.time_left() > 1.0:
                self.try_strategy('multi_local_search_final', self.strategy_multi_local_search)
        else:
            if EXPLORE_MODE == 'milp_probe':
                self.try_strategy('optional_milp_backend', self.strategy_optional_milp_backend)
            if EXPLORE_MODE == 'scarce_dual':
                self.try_strategy('scarce_dual_pair_cover', self.strategy_scarce_dual_pair_cover)
            if self.best_metrics and self.best_metrics['covered_count'] == n_tasks and (self.best_metrics['total_score'] <= 1514.318):
                return self.best_result
            self.try_strategy('pair_density_matching', self.strategy_pair_density_matching)
            self.try_strategy('pair_saving_matching', self.strategy_pair_saving_matching)
            self.try_strategy('pair_beam_matching', self.strategy_pair_beam_matching)
            self.try_strategy('pair_local_refine', self.strategy_pair_local_refine)
            self.try_strategy('scarce_subset_repair', self.strategy_scarce_subset_repair)
            self.try_strategy('scarce_exact_lns', self.strategy_scarce_exact_lns)
            self.try_strategy('scarce_pair_reshuffle', self.strategy_scarce_pair_reshuffle)
            self.try_strategy('scarce_exact_lns_after_reshuffle', self.strategy_scarce_exact_lns)
            self.try_strategy('scarce_random_lns', self.strategy_scarce_random_lns)
            if self.best_metrics and self.best_metrics['covered_count'] < n_tasks:
                density_result = self.strategy_pair_density_matching()
                if density_result:
                    m = self.evaluate(density_result)
                    if self.is_better(m, self.best_metrics):
                        self.best_result = density_result
                        self.best_metrics = m
        return self.best_result if self.best_result is not None else []

def solve(input_text: str) -> list:
    candidates = _parse_candidates(input_text)
    time_limit = 9.65 if EXPLORE_MODE == 'time_9_65' else 9.45
    agent = AutoSolverAgent(candidates, time_limit=time_limit)
    return agent.run()
