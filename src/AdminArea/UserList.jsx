import { useEffect, useState } from 'react';
import { Pencil, Trash2, Search } from 'lucide-react';
import axios from 'axios';
import Swal from 'sweetalert2';

const UserList = () => {
  const [users, setUsers] = useState(
    JSON.parse(localStorage.getItem('users')) || []
  );
  const currentUserMail = JSON.parse(localStorage.getItem('user')).email;
  const [editingUser, setEditingUser] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const deleteUser = async (email) => {
    Swal.fire({
      title: 'Are you sure?',
      text: "You won't be able to revert this!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#2563eb',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete it!',
      cancelButtonText: 'No, cancel!',
      reverseButtons: true,
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          const res = await axios.post('http://127.0.0.1:5000/deleteData', {
            name: 'users',
            key: email,
          });
          // alert(res.data.message);
          const updatedUsers = users.filter((user) => user.email !== email);
          setUsers(updatedUsers);
          localStorage.setItem('users', JSON.stringify(updatedUsers));
          Swal.fire({
            title: 'Deleted!',
            text: res.data.message,
            confirmButtonColor: '#2563eb',
            icon: 'success',
          });
        } catch (error) {
          console.error('Error calling Python function', error);
          Swal.fire('Error', error.response.data.error+'!', 'error');
        }
      } else if (
        /* Read more about handling dismissals below */
        result.dismiss === Swal.DismissReason.cancel
      ) {
        Swal.fire({
          title: 'Cancelled',
          text: 'Your imaginary user is safe :)',
          confirmButtonColor: '#2563eb',
          icon: 'error',
        });
      }
    });
  };

  const updateUser = async (e) => {
    e.preventDefault();
    Swal.fire({
      title: 'Do you want to save the changes?',
      showDenyButton: true,
      showCancelButton: true,
      confirmButtonText: 'Save',
      denyButtonText: `Don't save`,
      confirmButtonColor: '#2563eb',
    }).then(async (result) => {
      /* Read more about isConfirmed, isDenied below */
      if (result.isConfirmed) {
        try {
          const res = await axios.post('http://127.0.0.1:5000/updateData', {
            name: 'users',
            data: editingUser,
          });

          const updatedUsers = users.map((user) =>
            user.email === editingUser.email  
              ? {
                  ...user,
                  name: editingUser.name,
                  role: editingUser.role,
                  phoneNumber: editingUser.phoneNumber,
                }
              : user
          );

          localStorage.setItem('users', JSON.stringify(updatedUsers));
          setUsers(updatedUsers);
          setEditingUser(null);

          Swal.fire({
            title: res.data.success,
            icon: 'success',
            confirmButtonText: 'OK',
            confirmButtonColor: '#2563eb',
          });
        } catch (error) {
          console.log('Error calling Python function', error);
          Swal.fire('Saving failed', 'Please try again', 'error');
        }
      } else if (result.isDenied) {
        Swal.fire({
          title: 'Changes are not saved',
          icon: 'info',
          confirmButtonText: 'OK',
          confirmButtonColor: '#2563eb',
        });
      }
    });
  };
  const getList=async(value)=>{
    try {
        const res = await axios.post('http://127.0.0.1:5000/getData', {
          name:value
        });
        return(res.data.message);
      } catch (error) {
        console.error('Error calling Python function', error);
        return [];
      };
  }
  useEffect(() => {
    const fetchSchedules = async () => {
      const data = await getList('users');
      // if (Array.isArray(data))
      setUsers(data);
      // localStorage.setItem("users", JSON.stringify(data));
    };
    fetchSchedules();
  }, []);

  const handleEdit = (user) => setEditingUser(user);

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-300">User List</h2>
        <div className="flex items-center bg-gray-700 p-2 rounded-md shadow-md w-64">
          <Search className="text-gray-400 w-5 h-5 mr-2" />
          <input
            type="text"
            placeholder="Search users..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-transparent text-gray-200 border-none focus:outline-none"
          />
        </div>
      </div>

      <div className="table-container overflow-auto max-h-[70vh]">
        <table className="w-full border-collapse border border-gray-700 shadow-lg rounded-lg">
          <thead className="bg-gray-800 text-gray-300">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase">
                Phone
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase">
                Role
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className={'bg-gray-900 text--200 divide-y divide-gray-700'}>
            {filteredUsers.map((user,index) => (
              <tr
                key={index}
                className={
                  currentUserMail == user.email
                    ? 'bg-slate-700 '
                    : ' ' + '  transition-all hover:bg-gray-800 '
                }
              >
                <td className="px-6 py-4">{user.name}</td>
                <td className="px-6 py-4">{user.email}</td>
                <td className="px-6 py-4">{user.phoneNumber}</td>
                <td className="px-6 py-4">{user.role}</td>
                <td className="px-6 py-4 flex space-x-4 items-center justify-center">
                  <button
                    onClick={() => handleEdit(user)}
                    className="text-blue-400 hover:text-blue-600 transition-transform transform hover:scale-110"
                  >
                    <Pencil className="h-5 w-5" />
                  </button>
                  {currentUserMail != user.email ? (
                    <button
                      onClick={() => deleteUser(user.email)}
                      className="text-red-400 hover:text-red-600 transition-transform transform hover:scale-110"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  ) : (
                    ''
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editingUser && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-gradient-to-br from-gray-800 via-gray-900 to-black p-6 rounded-xl shadow-2xl w-96 backdrop-blur-md border border-gray-700">
            <h3 className="text-lg font-semibold text-gray-200 mb-4 text-center">
              Edit User
            </h3>
            <form onSubmit={updateUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400">
                  Name
                </label>
                <input
                  type="text"
                  value={editingUser.name}
                  onChange={(e) =>
                    setEditingUser({ ...editingUser, name: e.target.value })
                  }
                  className="w-full p-2 bg-gray-700 text-white border border-gray-600 rounded-md focus:ring-2 focus:ring-blue-400 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400">
                  Email
                </label>
                <input
                  type="email"
                  disabled
                  value={editingUser.email}
                  onChange={(e) =>
                    setEditingUser({ ...editingUser, email: e.target.value })
                  }
                  className="w-full p-2 bg-gray-700 text-white border border-gray-600 rounded-md focus:ring-2 focus:ring-blue-400 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400">
                  Phone
                </label>
                <input
                  type="tel"
                  value={editingUser.phoneNumber}
                  onChange={(e) =>
                    setEditingUser({
                      ...editingUser,
                      phoneNumber: e.target.value,
                    })
                  }
                  className="w-full p-2 bg-gray-700 text-white border border-gray-600 rounded-md focus:ring-2 focus:ring-blue-400 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400">
                  Role
                </label>
                <select
                  value={editingUser.role}
                  onChange={(e) =>
                    setEditingUser({ ...editingUser, role: e.target.value })
                  }
                  className="w-full p-2 bg-gray-700 text-white border border-gray-600 rounded-md focus:ring-2 focus:ring-blue-400 focus:outline-none"
                  disabled={currentUserMail == editingUser.email}
                >
                  <option value="student">Student</option>
                  <option value="teacher">Teacher</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div className="mt-4 flex justify-between">
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md shadow-md hover:bg-blue-700 transition-transform transform hover:scale-105"
                >
                  Save
                </button>
                <button
                  type="button"
                  onClick={() => setEditingUser(null)}
                  className="px-4 py-2 bg-gray-600 text-gray-300 rounded-md shadow-md hover:bg-gray-500 transition-transform transform hover:scale-105"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserList;
