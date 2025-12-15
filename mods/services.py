from .models import Mod, DLC

def check_compatibility(mod, user_version, user_dlc_ids, user_mod_ids=None):
    issues = []
    status = 'compatible'
    
    # 1. Check Game Version
    # Simple string comparison (In production, use semver)
    if user_version < mod.min_game_version:
        status = 'incompatible'
        issues.append({
            'type': 'version',
            'message': f"Requires game version {mod.min_game_version}+. You have {user_version}."
        })

    # 2. Check DLCs
    required_dlc_ids = set(mod.required_dlcs.values_list('id', flat=True))
    owned_dlc_ids = set(user_dlc_ids)
    missing_dlcs = required_dlc_ids - owned_dlc_ids
    
    if missing_dlcs:
        status = 'incompatible'
        missing_names = DLC.objects.filter(id__in=missing_dlcs).values_list('name', flat=True)
        issues.append({
            'type': 'dlc',
            'message': f"Missing required DLCs: {', '.join(missing_names)}."
        })

    # 3. Check Mod Conflicts (if user provided installed mods)
    if user_mod_ids:
        conflicts = mod.conflicts_with.filter(id__in=user_mod_ids)
        if conflicts.exists():
            status = 'warning' # Conflicts might be fixable with load order
            names = [c.title for c in conflicts]
            issues.append({
                'type': 'conflict',
                'message': f"Conflicts with installed mods: {', '.join(names)}."
            })

    return {'status': status, 'issues': issues}