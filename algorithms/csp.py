"""
Constraint Satisfaction Problem (CSP) Implementation
Uses Backtracking search with MRV (Minimum Remaining Values) heuristic
to select the optimal hospital based on constraints.
"""


def hospital_csp(hospitals, icu_required, emergency_node, city_graph):
    """
    Solve hospital selection as a Constraint Satisfaction Problem.

    Variable: Hospital assignment
    Domain: List of available hospitals
    Constraints:
        1. Hospital must have available bed (available_beds > 0)
        2. ICU must be available if required (icu_available == True)
        3. Doctor must be available (doctors_available > 0)
        4. Capacity must not exceed limit

    Uses Backtracking with MRV heuristic (hospitals with fewest
    remaining valid options are tried first).

    Args:
        hospitals (list[Hospital]): List of all hospitals.
        icu_required (bool): Whether ICU is required.
        emergency_node (str): The emergency location node.
        city_graph (CityGraph): City graph for distance calculations.

    Returns:
        dict: {
            'assigned_hospital': Hospital or None,
            'steps': list of step dicts showing the CSP solving process,
            'domain_reductions': list showing domain after each constraint,
            'backtrack_count': number of backtracks,
            'constraints': list of constraint descriptions,
        }
    """
    steps = []
    domain_reductions = []
    backtrack_count = 0

    # Define constraints
    constraints = [
        "C1: Hospital must have available beds (available_beds > 0)",
        "C2: ICU must be available (if required)",
        "C3: Doctor must be available (doctors_available > 0)",
        "C4: Capacity must not exceed limit",
    ]

    # Step 1: Initial domain = all hospitals
    initial_domain = [h.name for h in hospitals]
    steps.append({
        'step': 1,
        'action': 'Initialize Domain',
        'description': f'Initial domain contains all {len(hospitals)} hospitals',
        'domain': initial_domain.copy(),
        'status': 'info',
    })
    domain_reductions.append({
        'stage': 'Initial',
        'domain': initial_domain.copy(),
        'removed': [],
        'reason': 'All hospitals in domain',
    })

    # Step 2: Apply constraint C1 - Bed availability
    current_domain = []
    removed_c1 = []
    for h in hospitals:
        if h.available_beds > 0:
            current_domain.append(h)
        else:
            removed_c1.append(h.name)

    domain_names = [h.name for h in current_domain]
    steps.append({
        'step': 2,
        'action': 'Apply C1: Bed Availability',
        'description': f'Checking available_beds > 0. Removed: {removed_c1 if removed_c1 else "None"}',
        'domain': domain_names.copy(),
        'removed': removed_c1,
        'status': 'constraint_check',
    })
    domain_reductions.append({
        'stage': 'After C1 (Beds)',
        'domain': domain_names.copy(),
        'removed': removed_c1,
        'reason': 'No available beds',
    })

    # Step 3: Apply constraint C2 - ICU availability (if required)
    if icu_required:
        filtered = []
        removed_c2 = []
        for h in current_domain:
            if h.icu_available:
                filtered.append(h)
            else:
                removed_c2.append(h.name)
        current_domain = filtered
        domain_names = [h.name for h in current_domain]

        steps.append({
            'step': 3,
            'action': 'Apply C2: ICU Availability',
            'description': f'ICU required. Checking icu_available == True. Removed: {removed_c2 if removed_c2 else "None"}',
            'domain': domain_names.copy(),
            'removed': removed_c2,
            'status': 'constraint_check',
        })
        domain_reductions.append({
            'stage': 'After C2 (ICU)',
            'domain': domain_names.copy(),
            'removed': removed_c2,
            'reason': 'ICU not available',
        })
    else:
        steps.append({
            'step': 3,
            'action': 'Skip C2: ICU Not Required',
            'description': 'ICU not required for this emergency. Constraint skipped.',
            'domain': [h.name for h in current_domain],
            'removed': [],
            'status': 'skipped',
        })
        domain_reductions.append({
            'stage': 'After C2 (ICU - Skipped)',
            'domain': [h.name for h in current_domain],
            'removed': [],
            'reason': 'ICU not required',
        })

    # Step 4: Apply constraint C3 - Doctor availability
    filtered = []
    removed_c3 = []
    for h in current_domain:
        if h.doctors_available > 0:
            filtered.append(h)
        else:
            removed_c3.append(h.name)
    current_domain = filtered
    domain_names = [h.name for h in current_domain]

    steps.append({
        'step': 4,
        'action': 'Apply C3: Doctor Availability',
        'description': f'Checking doctors_available > 0. Removed: {removed_c3 if removed_c3 else "None"}',
        'domain': domain_names.copy(),
        'removed': removed_c3,
        'status': 'constraint_check',
    })
    domain_reductions.append({
        'stage': 'After C3 (Doctors)',
        'domain': domain_names.copy(),
        'removed': removed_c3,
        'reason': 'No doctors available',
    })

    # Step 5: Apply constraint C4 - Capacity limit
    filtered = []
    removed_c4 = []
    for h in current_domain:
        if (h.total_beds - h.available_beds) < h.capacity_limit:
            filtered.append(h)
        else:
            removed_c4.append(h.name)
    current_domain = filtered
    domain_names = [h.name for h in current_domain]

    steps.append({
        'step': 5,
        'action': 'Apply C4: Capacity Limit',
        'description': f'Checking capacity not exceeded. Removed: {removed_c4 if removed_c4 else "None"}',
        'domain': domain_names.copy(),
        'removed': removed_c4,
        'status': 'constraint_check',
    })
    domain_reductions.append({
        'stage': 'After C4 (Capacity)',
        'domain': domain_names.copy(),
        'removed': removed_c4,
        'reason': 'Capacity exceeded',
    })

    # Step 6: Backtracking search with MRV
    if not current_domain:
        steps.append({
            'step': 6,
            'action': 'Backtracking: No Solution',
            'description': 'Domain is empty after constraint propagation. No valid hospital found.',
            'domain': [],
            'status': 'failure',
        })
        return {
            'assigned_hospital': None,
            'steps': steps,
            'domain_reductions': domain_reductions,
            'backtrack_count': 0,
            'constraints': constraints,
        }

    # MRV: Sort by remaining capacity (fewer resources = try first to reduce backtracking)
    # Then apply backtracking to select the best hospital considering distance
    steps.append({
        'step': 6,
        'action': 'Apply MRV Heuristic',
        'description': 'Ordering domain by Minimum Remaining Values (available beds ascending)',
        'domain': domain_names.copy(),
        'status': 'heuristic',
    })

    # Sort by MRV (fewer available beds first - most constrained)
    mrv_sorted = sorted(current_domain, key=lambda h: h.available_beds)
    mrv_names = [h.name for h in mrv_sorted]

    steps.append({
        'step': 7,
        'action': 'MRV Ordering Result',
        'description': f'Order: {mrv_names}',
        'domain': mrv_names,
        'status': 'info',
    })

    # Backtracking: Try each hospital in MRV order
    # Additional constraint: select closest valid hospital
    assigned = None
    best_distance = float('inf')

    for i, hospital in enumerate(mrv_sorted):
        distance = city_graph.euclidean_distance(emergency_node, hospital.node)

        steps.append({
            'step': 8 + i,
            'action': f'Backtracking: Try {hospital.name}',
            'description': (
                f'Testing {hospital.name} (node {hospital.node}): '
                f'distance={distance:.2f}, beds={hospital.available_beds}, '
                f'ICU={"Yes" if hospital.icu_available else "No"}, '
                f'doctors={hospital.doctors_available}'
            ),
            'domain': [hospital.name],
            'status': 'trying',
        })

        # All constraints already satisfied, pick closest
        if distance < best_distance:
            if assigned is not None:
                backtrack_count += 1
                steps.append({
                    'step': 8 + i,
                    'action': f'Backtrack from {assigned.name}',
                    'description': f'{hospital.name} is closer ({distance:.2f} < {best_distance:.2f}). Backtracking.',
                    'domain': [hospital.name],
                    'status': 'backtrack',
                })
            best_distance = distance
            assigned = hospital

    # Final assignment
    if assigned:
        steps.append({
            'step': len(steps) + 1,
            'action': 'Assignment Complete',
            'description': f'Assigned hospital: {assigned.name} at node {assigned.node} (distance: {best_distance:.2f})',
            'domain': [assigned.name],
            'status': 'success',
        })

    return {
        'assigned_hospital': assigned,
        'steps': steps,
        'domain_reductions': domain_reductions,
        'backtrack_count': backtrack_count,
        'constraints': constraints,
    }
