# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#     Copyright 2020 QandA-vietnam.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Allow access if user is an owner of object
    """
    def has_object_permission(self, request, view, obj):
        return bool(request.user == obj.owner)
